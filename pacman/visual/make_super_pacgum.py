import pygame

pygame.init()

super_pacgum_surface = pygame.Surface((64, 64), pygame.SRCALPHA)

middle_y = super_pacgum_surface.get_height() // 2
middle_x = super_pacgum_surface.get_width() // 2

pygame.draw.circle(
    super_pacgum_surface,
    (255, 255, 180),
    (middle_x, middle_y),
    32
)

pygame.image.save(
    super_pacgum_surface,
    "assets/other/super_pacgum.png",
)

pacgum_surface = pygame.Surface((64, 64), pygame.SRCALPHA)

middle_y = pacgum_surface.get_height() // 2
middle_x = pacgum_surface.get_width() // 2

pygame.draw.circle(
    pacgum_surface,
    (255, 255, 255),
    (middle_x, middle_y),
    32
)

pygame.image.save(
    pacgum_surface,
    "assets/other/dot.png",
)
