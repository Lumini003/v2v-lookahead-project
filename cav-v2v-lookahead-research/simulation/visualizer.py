import pygame
import scenario
import config
from simulation.context import ScenarioContext


MARGIN = 40


def road_geometry(surface, road_length, num_lanes):
    width = surface.get_width()
    height = surface.get_height()
    lane_w = config.LANE_WIDTH_UNITS
    fit_width = (width - 2 * MARGIN) / road_length
    fit_height = (height - 2 * MARGIN) / (num_lanes * lane_w)
    scale = min(fit_width, fit_height, config.PIXELS_PER_UNIT)
    road_length_px = road_length * scale
    road_height_px = num_lanes * lane_w * scale
    road_left = (width - road_length_px) // 2
    road_top = (height - road_height_px) // 2
    lane_h_px = lane_w * scale
    return road_left, road_top, road_length_px, road_height_px, lane_h_px, scale


def draw_road(
    surface, road_left, road_top, road_length_px, road_height_px, lane_h_px, num_lanes
):
    road_rect = pygame.Rect(road_left, road_top, road_length_px, road_height_px)
    pygame.draw.rect(surface, config.ROAD_COLOR, road_rect)

    if num_lanes >= 2:
        center_y = road_top + road_height_px // 2
        x = road_left
        while x < road_left + road_length_px:
            seg_end = min(x + 24, road_left + road_length_px)
            pygame.draw.line(
                surface,
                config.CENTER_LINE_COLOR,
                (x, center_y),
                (seg_end, center_y),
                width=3,
            )
            x += 40

    for i in range(1, num_lanes):
        y = road_top + i * lane_h_px
        pygame.draw.line(
            surface,
            config.LANE_LINE_COLOR,
            (road_left, y),
            (road_left + road_length_px, y),
            width=3,
        )

    pygame.draw.line(
        surface,
        config.LANE_LINE_COLOR,
        (road_left, road_top),
        (road_left, road_top + road_height_px),
        width=2,
    )
    pygame.draw.line(
        surface,
        config.LANE_LINE_COLOR,
        (road_left + road_length_px, road_top),
        (road_left + road_length_px, road_top + road_height_px),
        width=2,
    )


def draw_labels(surface, road_left, road_top, road_length_px, road_height_px):
    try:
        font = pygame.font.Font(None, 36)
    except Exception:
        font = pygame.font.SysFont("Arial", 24)
    a_text = font.render("Point A", True, config.LABEL_COLOR)
    b_text = font.render("Point B", True, config.LABEL_COLOR)
    a_rect = a_text.get_rect(centerx=road_left, top=road_top - 28)
    b_rect = b_text.get_rect(centerx=road_left + road_length_px, top=road_top - 28)
    surface.blit(a_text, a_rect)
    surface.blit(b_text, b_rect)


def draw_cars(surface, cars, road_left, road_top, lane_h_px, scale):
    car_w = config.CAR_LENGTH_UNITS * scale
    car_h = lane_h_px * 0.7
    for car in cars:
        car_len_px = car.length * scale
        x = road_left + car.position * scale - car_len_px / 2
        y = road_top + car.lane * lane_h_px + (lane_h_px - car_h) / 2
        color = (
            config.CAR_COLORS[car.color]
            if 0 <= car.color < len(config.CAR_COLORS)
            else config.CAR_COLORS[0]
        )
        pygame.draw.rect(surface, color, (x, y, car_len_px, car_h))


def draw_ui(surface, started, paused):
    try:
        font = pygame.font.Font(None, 28)
    except Exception:
        font = pygame.font.SysFont("Arial", 20)
    if not started:
        text = font.render("Press SPACE to start", True, config.LABEL_COLOR)
    elif paused:
        text = font.render(
            "Paused — SPACE to resume | R to restart", True, config.LABEL_COLOR
        )
    else:
        text = font.render(
            "Running — SPACE to pause | R to restart", True, config.LABEL_COLOR
        )
    r = text.get_rect(bottomleft=(10, surface.get_height() - 8))
    surface.blit(text, r)


def run():
    pygame.init()
    screen = pygame.display.set_mode(
        (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE
    )
    pygame.display.set_caption("CAV V2V Lookahead")
    clock = pygame.time.Clock()

    def reset():
        ctx = ScenarioContext()
        scenario.reset()
        return ctx, 0.0, []

    sim_ctx, sim_time, active_cars = reset()
    started = False
    paused = False
    running = True

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if not started:
                        started = True
                        paused = False
                    else:
                        paused = not paused
                elif event.key == pygame.K_r:
                    sim_ctx, sim_time, active_cars = reset()
                    started = False
                    paused = False

        sim_ctx._pending = []
        scenario.setup(sim_ctx, sim_time)
        if started and not paused:
            for car in sim_ctx._pending:
                if car not in active_cars:
                    active_cars.append(car)
            sim_time += dt
            for car in active_cars:
                car.update(dt, sim_ctx.road_length, active_cars, sim_time)
            active_cars = [c for c in active_cars if c.front < sim_ctx.road_length]

        road_left, road_top, road_length_px, road_height_px, lane_h_px, scale = (
            road_geometry(screen, sim_ctx.road_length, sim_ctx.num_lanes)
        )
        screen.fill(config.BACKGROUND_COLOR)
        draw_road(
            screen,
            road_left,
            road_top,
            road_length_px,
            road_height_px,
            lane_h_px,
            sim_ctx.num_lanes,
        )
        draw_labels(screen, road_left, road_top, road_length_px, road_height_px)
        draw_cars(screen, active_cars, road_left, road_top, lane_h_px, scale)
        draw_ui(screen, started, paused)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
