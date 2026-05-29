# R Script Explanation — `full_analysis.R`

> This file explains **every section** of the R script so you can understand and defend each line in your viva.

---

## Step 0: Load & Merge Data

```r
files <- list.files(pattern = "scenario_.*_results\\.csv", full.names = TRUE)
data <- do.call(rbind, lapply(files, read.csv))
```

| Function | What it does |
|----------|-------------|
| `list.files(pattern = ...)` | Finds all files matching the pattern `scenario_X_results.csv` in the working directory |
| `lapply(files, read.csv)` | Reads each CSV into a separate dataframe, storing them in a list |
| `do.call(rbind, ...)` | Stacks all dataframes vertically (row-bind) into one combined dataframe |

**Result**: One dataframe with **2,940 rows** (7 files × 420 rows each).

```r
data$LookAheadRange <- ifelse(data$Lane_Type == "Human", 0,
                               as.numeric(gsub("LAR_", "", data$Lane_Type)))
```

| Part | What it does |
|------|-------------|
| `gsub("LAR_", "", ...)` | Removes the text "LAR_" from values like "LAR_3", leaving just "3" |
| `as.numeric(...)` | Converts the string "3" to the number 3 |
| `ifelse(... == "Human", 0, ...)` | Assigns 0 to Human (no V2V look-ahead) |

**Why**: `Lane_Type` is a text label. For regression and plotting we need a **numeric** variable (0, 1, 2, 3, 4, 5).

```r
data$DriverType <- as.factor(ifelse(data$Lane_Type == "Human", "Human", "Automated"))
```

**Why**: Groups all LAR levels into one "Automated" category for the Human vs AV comparison (t-test). `as.factor()` tells R to treat it as a **categorical** variable, not text.

---

## Part A: Descriptive Analytics

### Step 1: Summary Statistics

```r
aggregate(cbind(SpeedVariance, StabilityMargin, StabilizationTime) ~ Lane_Type,
          data = data, FUN = function(x) c(Mean=mean(x), SD=sd(x), ...))
```

| Function | What it does |
|----------|-------------|
| `aggregate(... ~ Lane_Type)` | Splits the data by `Lane_Type` and applies a function to each group |
| `cbind(...)` | Bundles multiple columns so we can summarise all three DVs at once |
| `mean(x)` | Arithmetic average — **central tendency** |
| `sd(x)` | Standard deviation — **spread/consistency** |
| `median(x)` | Middle value — robust to outliers unlike the mean |

**Why we report both Mean and SD**: A low mean with high SD means "good on average but inconsistent." Both are needed to claim reliable stability.

---

### Step 2: Boxplots

```r
boxplot(SpeedVariance ~ Lane_Type, data = data, col = ...)
```

**What each part of the boxplot means**:
- **Thick line in the middle** = Median (50th percentile)
- **Box** = Interquartile Range (IQR) — where the middle 50% of data falls
- **Whiskers** = Extend to 1.5 × IQR from the box edges
- **Dots beyond whiskers** = Outliers

```r
abline(h = 1, col = "red", lty = 2)
```

**Why**: For the Stability Margin plot, the red dashed line at 1.0 marks the **string stability boundary**. Above 1 = unstable (disturbance amplifies). Below 1 = stable.

---

### Step 2b: Histograms

```r
hist(data$SpeedVariance[data$Lane_Type == lt], breaks = 20)
```

**Why**: Histograms show the **shape** of the distribution — is it bell-shaped (normal)? Skewed? Bimodal? This previews whether parametric tests are appropriate.

---

### Step 2c: Diminishing Returns Line Plot

```r
means_av <- aggregate(SpeedVariance ~ LookAheadRange, data = av_data, FUN = mean)
plot(means_av$LookAheadRange, means_av$SpeedVariance, type = "b")
```

| Argument | Meaning |
|----------|---------|
| `type = "b"` | "Both" — draws points AND connecting lines |
| `pch = 19` | Filled circle marker |

**Why this plot matters**: It's the **visual evidence** of diminishing returns. The curve should drop steeply from 1→3 then flatten from 3→5.

---

### Step 3: % Improvement Calculation

```r
pct <- ((prev - curr) / prev) * 100
```

**Formula**: `(Value_before - Value_after) / Value_before × 100`

This gives the **relative improvement** at each step. A decreasing percentage directly demonstrates diminishing returns.

---

## Part B: Inferential Analytics

### Step 4a: Shapiro-Wilk Normality Test

```r
shapiro.test(sv)
```

| Output | Meaning |
|--------|---------|
| `W` statistic | Ranges from 0 to 1. Closer to 1 = more normal |
| `p-value` | p > 0.05 → data is consistent with normality; p < 0.05 → deviates from normality |

**Why we test this**: The t-test and ANOVA assume the data comes from a normal distribution. If violated, we either use non-parametric tests or invoke the **Central Limit Theorem** (valid when n > 30).

### Step 4a (cont): Q-Q Plots

```r
qqnorm(...)   # Plots sample quantiles vs theoretical normal quantiles
qqline(...)   # Adds the reference line
```

**How to read**: If points follow the diagonal line → data is normal. Deviations at the tails indicate heavy tails (more extreme values than expected).

### Step 4b: Levene's Test

```r
library(car)
leveneTest(SpeedVariance ~ Lane_Type, data = data)
```

**What it tests**: Whether the **variance** is equal across all groups (homoscedasticity).
- p > 0.05 → Variances are equal → ANOVA assumption met
- p < 0.05 → Variances differ → Use Welch's ANOVA or note the violation

**Why `car` package**: Levene's test isn't in base R. The `car` package provides it.

---

### Step 5: Welch's t-test

```r
t.test(human_sm, auto_sm, var.equal = FALSE)
```

| Argument | Meaning |
|----------|---------|
| `var.equal = FALSE` | Uses **Welch's** correction (doesn't assume equal variances) |
| If we set `TRUE` | Would use Student's t-test (assumes equal variances) |

**Output explained**:

| Output | Meaning |
|--------|---------|
| `t` | How many standard errors apart the two means are |
| `df` | Degrees of freedom (Welch's adjusts this — may not be a whole number) |
| `p-value` | Probability of seeing this difference if H₀ were true |
| `95% confidence interval` | Range for the true difference in means |
| `sample estimates` | The two group means |

**Cohen's d calculation**:
```r
cohens_d <- (mean(group1) - mean(group2)) / pooled_sd
```
- |d| < 0.2 = negligible
- |d| 0.2–0.5 = small
- |d| 0.5–0.8 = medium
- |d| > 0.8 = **large** (what we expect)

---

### Step 6: One-Way ANOVA

```r
anova_sv <- aov(SpeedVariance ~ LookAheadRange_factor, data = av_data)
summary(anova_sv)
```

| Part | What it does |
|------|-------------|
| `aov(DV ~ IV)` | Fits the ANOVA model |
| `summary()` | Displays the ANOVA table |

**ANOVA table explained**:

| Column | Meaning |
|--------|---------|
| `Df` | Degrees of freedom (between-groups = k−1; within-groups = N−k) |
| `Sum Sq` | Sum of squares — total variation attributed to the factor vs residual |
| `Mean Sq` | Sum Sq / Df |
| `F value` | Mean Sq (between) / Mean Sq (within) — the test statistic |
| `Pr(>F)` | p-value — if < 0.05, at least one group mean is different |

**Eta-squared** (effect size):
```r
eta_sq <- SS_between / SS_total
```
- η² > 0.01 = small, > 0.06 = medium, > 0.14 = **large**

---

### Step 7: Tukey's HSD

```r
TukeyHSD(anova_sv)
```

**Output explained (each row = one pair)**:

| Column | Meaning |
|--------|---------|
| `diff` | Difference in means (Group2 − Group1) |
| `lwr` | Lower bound of 95% CI |
| `upr` | Upper bound of 95% CI |
| `p adj` | **Adjusted** p-value (accounts for multiple comparisons) |

**Key rule**: If the CI includes 0, the difference is NOT significant.

```r
plot(tukey_sv)
```

**How to read the Tukey plot**: Each horizontal line represents a pair. If the line **crosses the vertical dashed line at 0**, that pair is NOT significantly different.

---

### Step 8: F-test for Variance

```r
var.test(human_sv, auto_sv)
```

| Output | Meaning |
|--------|---------|
| `F` | Ratio of the two variances (larger / smaller) |
| `p-value` | If < 0.05, variances are significantly different |

**Why this matters**: Shows Human drivers are not just worse on average, but more **unpredictable** (higher variance = higher risk).

---

## Part C: Predictive Analytics

### Step 10: Simple Linear Regression

```r
model_linear <- lm(SpeedVariance ~ LAR_numeric, data = av_data)
summary(model_linear)
```

| Function | What it does |
|----------|-------------|
| `lm(y ~ x)` | Fits a linear model using Ordinary Least Squares (OLS) |
| `summary()` | Shows coefficients, R², F-statistic, p-values |

**Output explained**:

| Row | Meaning |
|-----|---------|
| `(Intercept)` | β₀ — predicted Speed Variance when LAR = 0 |
| `LAR_numeric` | β₁ — change in Speed Variance per 1-unit increase in LAR |
| `Std. Error` | Uncertainty in each coefficient |
| `t value` | Coefficient / Std Error — tests if the coefficient ≠ 0 |
| `Pr(>\|t\|)` | p-value for each coefficient |
| `Multiple R-squared` | Proportion of DV variance explained by the model |
| `Adjusted R-squared` | R² adjusted for number of predictors (use this for comparison) |
| `F-statistic` | Tests if the overall model is significant |

---

### Step 11: Quadratic Regression

```r
model_quad <- lm(SpeedVariance ~ LAR_numeric + I(LAR_numeric^2), data = av_data)
```

| Part | Meaning |
|------|---------|
| `I(LAR_numeric^2)` | The `I()` function tells R to treat `^2` as "square this variable", not as a formula operator |
| Without `I()` | R would interpret `^` as an interaction term, not squaring |

**The three coefficients**:
- **β₀**: Intercept
- **β₁**: Linear effect (initial rate of decrease)
- **β₂**: Quadratic effect — **if positive and significant, the curve flattens** = mathematical proof of diminishing returns

---

### Step 12: Multiple Linear Regression

```r
model_multi <- lm(SpeedVariance ~ LAR_numeric + DriverType, data = data)
```

**Why**: Tests both predictors simultaneously. The coefficient for `DriverType` tells us the effect of being automated **after accounting for LAR**. Uses the full dataset (including Human).

---

### Step 13: Diagnostic Plots

```r
par(mfrow = c(2, 2))
plot(model_quad)
```

| Plot # | Name | What it checks | Good result |
|--------|------|---------------|-------------|
| 1 | Residuals vs Fitted | Linearity, constant variance | Random scatter around 0, no pattern |
| 2 | Normal Q-Q | Normality of residuals | Points on the diagonal |
| 3 | Scale-Location | Homoscedasticity | Horizontal band, no fan shape |
| 4 | Residuals vs Leverage | Influential outliers | No points beyond Cook's distance lines |

**Fitted vs Actual plot**: Shows how well the linear (red dashed) and quadratic (green solid) curves fit the actual data points.

---

### Step 14: Model Comparison

```r
AIC(model_linear, model_quad, model_multi)
```

| Metric | Rule | Why |
|--------|------|-----|
| **AIC** | Lower = better | Balances fit quality against model complexity |
| **Adjusted R²** | Higher = better | R² penalised for adding predictors that don't help |

**Decision**: The model with the lowest AIC **and** highest Adjusted R² is the best. If they disagree, prefer AIC (it has stronger theoretical foundation).

---

## Utility Functions Summary

| R Function | Purpose | Package |
|------------|---------|---------|
| `read.csv()` | Read CSV file | base |
| `rbind()` | Stack dataframes vertically | base |
| `aggregate()` | Group-by summary statistics | base |
| `boxplot()` | Create boxplots | base |
| `hist()` | Create histograms | base |
| `shapiro.test()` | Normality test | base |
| `leveneTest()` | Equal variance test | **car** |
| `t.test()` | Two-sample t-test | base |
| `aov()` | One-way ANOVA | base |
| `TukeyHSD()` | Post-hoc pairwise comparisons | base |
| `var.test()` | F-test for variance | base |
| `lm()` | Linear regression (simple/multiple/polynomial) | base |
| `AIC()` | Akaike Information Criterion | base |
| `qqnorm()`, `qqline()` | Q-Q normality plot | base |
| `plot(model)` | Regression diagnostic plots | base |
