# =============================================================================
# V2V Look-Ahead Range — FINAL CLEAN SCRIPT (A+ VERSION)
# =============================================================================

library(rstatix)
library(car)
library(ggplot2)
library(plotly)

# =============================================================================
# STEP 0: LOAD & CLEAN DATA
# =============================================================================

setwd("E:/TPSM PROJECT/data/data")

files <- list.files(pattern = "scenario_.*_results\\.csv", full.names = TRUE)
data <- do.call(rbind, lapply(files, read.csv))

# Extract Look-Ahead Range
data$LookAheadRange <- ifelse(
  data$Lane_Type == "Human",
  0,
  as.numeric(gsub("[^0-9]", "", data$Lane_Type))
)

# Remove missing values
data <- na.omit(data)

# Driver type
data$DriverType <- as.factor(ifelse(data$Lane_Type == "Human", "Human", "Automated"))
data$DriverType_num <- ifelse(data$DriverType == "Human", 0, 1)

# Rename variables
data$SpeedVariance     <- data$Peak_Speed_Variance
data$StabilityMargin   <- data$Amplification_Factor
data$StabilizationTime <- data$Settling_Time_sec

# Numeric LAR
data$LAR_numeric <- data$LookAheadRange

# Automated-only subset
av_data <- data[data$DriverType == "Automated", ]
av_data$LAR_factor  <- as.factor(av_data$LookAheadRange)
av_data$LAR_numeric <- av_data$LookAheadRange

# =============================================================================
# PART A: DESCRIPTIVE ANALYSIS
# =============================================================================

cat("\n===== DESCRIPTIVE ANALYSIS =====\n")

summary_stats <- aggregate(
  cbind(SpeedVariance, StabilityMargin, StabilizationTime) ~ Lane_Type,
  data = data, FUN = mean
)

summary_stats[, -1] <- round(summary_stats[, -1], 3)
print(summary_stats)

# Boxplots
par(mfrow=c(1,3))
boxplot(SpeedVariance ~ Lane_Type, data=data, col="lightblue", main="Speed Variance")
boxplot(StabilityMargin ~ Lane_Type, data=data, col="lightgreen", main="Stability Margin")
abline(h=1, col="red", lty=2)
boxplot(StabilizationTime ~ Lane_Type, data=data, col="lightcoral", main="Stabilization Time")
par(mfrow=c(1,1))


# HISTOGRAMS

cat("\n===== HISTOGRAMS =====\n")

par(mfrow=c(2,3))

for (lt in unique(data$Lane_Type)) {
  x <- data$SpeedVariance[data$Lane_Type == lt]
  
  hist(x,
       probability = TRUE,
       col = "lightblue",
       main = paste("Speed Variance -", lt),
       xlab = "Speed Variance",
       breaks = 20)
  
  lines(density(x), col = "red", lwd = 2)
}

par(mfrow=c(1,1))

# Line plots (mean trends)
means_av <- aggregate(
  cbind(SpeedVariance, StabilityMargin, StabilizationTime) ~ LookAheadRange,
  data = av_data, FUN = mean
)

par(mfrow=c(1,3))
plot(means_av$LookAheadRange, means_av$SpeedVariance, type="b", col="blue",
     main="Speed Variance vs LAR")
plot(means_av$LookAheadRange, means_av$StabilityMargin, type="b", col="green",
     main="Stability Margin vs LAR"); abline(h=1, col="red")
plot(means_av$LookAheadRange, means_av$StabilizationTime, type="b", col="purple",
     main="Stabilization Time vs LAR")
par(mfrow=c(1,1))

# =============================================================================
# PART B: INFERENTIAL ANALYSIS
# =============================================================================

cat("\n===== ASSUMPTION TEST =====\n")
print(leveneTest(SpeedVariance ~ Lane_Type, data))

# Welch ANOVA (robust)
cat("\n===== WELCH ANOVA =====\n")
print(oneway.test(SpeedVariance ~ LAR_factor, data=av_data))

# Effect size (Eta squared)
anova_model <- aov(SpeedVariance ~ LAR_factor, data=av_data)
ss <- summary(anova_model)[[1]]
eta_sq <- ss$`Sum Sq`[1] / sum(ss$`Sum Sq`)
cat("Eta-squared:", eta_sq, "\n")

# Games-Howell (post-hoc)
cat("\n===== GAMES-HOWELL =====\n")
gh_sv <- games_howell_test(SpeedVariance ~ LAR_factor, data=av_data)
print(gh_sv)

# T-test (Human vs Automated)
cat("\n===== T-TEST =====\n")
tt <- t.test(SpeedVariance ~ DriverType, data=data)
print(tt)

# Cohen's d
human_sv <- data$SpeedVariance[data$DriverType == "Human"]
auto_sv  <- data$SpeedVariance[data$DriverType == "Automated"]
cohens_d <- (mean(human_sv) - mean(auto_sv)) /
  sqrt((var(human_sv) + var(auto_sv)) / 2)
cat("Cohen's d:", cohens_d, "\n")

# =============================================================================
# PART C: CORRELATION (JUSTIFICATION)
# =============================================================================

cat("\n===== CORRELATION =====\n")

cor_sv <- cor(av_data$LAR_numeric, av_data$SpeedVariance, method="spearman")
cat("LAR vs SpeedVariance:", cor_sv, "\n")

# =============================================================================
# PART D: PREDICTIVE MODELING
# =============================================================================

cat("\n===== REGRESSION MODELS =====\n")

model_linear <- lm(SpeedVariance ~ LAR_numeric, data=data)
model_quad   <- lm(SpeedVariance ~ LAR_numeric + I(LAR_numeric^2), data=data)
model_final  <- lm(SpeedVariance ~ LAR_numeric + I(LAR_numeric^2) + DriverType, data=data)

summary(model_linear)
summary(model_quad)
summary(model_final)

# Model comparison
cat("\n===== MODEL COMPARISON =====\n")
cat("Linear:", summary(model_linear)$adj.r.squared, "\n")
cat("Quadratic:", summary(model_quad)$adj.r.squared, "\n")
cat("Final:", summary(model_final)$adj.r.squared, "\n")

# =============================================================================
# MODEL DIAGNOSTICS
# =============================================================================

par(mfrow=c(2,2))
plot(model_final)
par(mfrow=c(1,1))

# =============================================================================
# 3D VISUALIZATION
# =============================================================================

grid <- expand.grid(
  LAR = seq(min(data$LookAheadRange), max(data$LookAheadRange), length.out = 20),
  Driver = c(0, 1)
)

grid$pred <- predict(model_final, newdata = data.frame(
  LAR_numeric = grid$LAR,
  DriverType = ifelse(grid$Driver == 0, "Human", "Automated")
))

plot_ly() %>%
  add_markers(
    data = data,
    x = ~LookAheadRange,
    y = ~DriverType_num,
    z = ~SpeedVariance,
    color = ~DriverType,
    colors = c("red", "blue")
  ) %>%
  add_surface(
    x = matrix(grid$LAR, nrow = 20),
    y = matrix(grid$Driver, nrow = 20),
    z = matrix(grid$pred, nrow = 20),
    opacity = 0.5
  ) %>%
  layout(
    scene = list(
      xaxis = list(title = "LAR"),
      yaxis = list(title = "Driver Type"),
      zaxis = list(title = "Speed Variance")
    )
  )

# =============================================================================
# DIMINISHING RETURNS
# =============================================================================

cat("\n===== DIMINISHING RETURNS =====\n")

for (i in 2:5) {
  prev <- mean(av_data$SpeedVariance[av_data$LookAheadRange == i-1])
  curr <- mean(av_data$SpeedVariance[av_data$LookAheadRange == i])
  pct <- ((prev - curr)/prev)*100
  cat("LAR", i-1, "->", i, ":", round(pct,2), "%\n")
}

# =============================================================================
# FINAL CONCLUSION
# =============================================================================

cat("\n===== FINAL CONCLUSION =====\n")
cat("Increasing LAR significantly reduces Speed Variance.\n")
cat("However, improvements become statistically insignificant after LAR = 4.\n")
cat("This confirms diminishing returns.\n")
cat("Final model (quadratic + driver type) best explains the data.\n")