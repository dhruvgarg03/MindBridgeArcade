import pygame

class Tooltip:
    def __init__(self):
        font = pygame.font.Font('freesansbold.ttf', 15)
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_rect = pygame.Rect(200, 150, 400, 200)
        self.tooltip_close_rect = pygame.Rect(200 + 370, 150 + 10, 20, 20)
        self.font = font

    def show(self, text):
        self.tooltip_text = text
        self.show_tooltip = True

    def hide(self):
        self.show_tooltip = False

    def handle_event(self, event):
        if self.show_tooltip and event.type == pygame.MOUSEBUTTONDOWN:
            if self.tooltip_close_rect.collidepoint(event.pos):
                self.hide()

    def draw(self, screen):
        if self.show_tooltip:
            # Box background
            pygame.draw.rect(screen, (50, 50, 50), self.tooltip_rect, border_radius=10)
            # Border
            pygame.draw.rect(screen, (200, 200, 200), self.tooltip_rect, 2, border_radius=10)
            # Close "X" button
            pygame.draw.rect(screen, (200, 50, 50), self.tooltip_close_rect, border_radius=5)
            x_text = self.font.render('X', True, (255, 255, 255))
            screen.blit(x_text, (self.tooltip_close_rect.x + 5, self.tooltip_close_rect.y + 2))

            # Wrap and render the tooltip text
            wrapped_lines = []
            words = self.tooltip_text.split()
            line = ""
            for word in words:
                if self.font.size(line + word)[0] < self.tooltip_rect.width - 40:
                    line += word + " "
                else:
                    wrapped_lines.append(line)
                    line = word + " "
            wrapped_lines.append(line)

            for idx, l in enumerate(wrapped_lines):
                text_surf = self.font.render(l.strip(), True, (255, 255, 255))
                screen.blit(text_surf, (self.tooltip_rect.x + 20, self.tooltip_rect.y + 50 + idx * 30))
