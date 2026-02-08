import pygame

class Button:
    def __init__(self, x_cord, y_cord, text="", width=60, height=30):
        self.clock = 0
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.width = width
        self.height = height
        self.txt = text
        self.delay = 0.2
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width , self.height)
        self.label_text = pygame.font.Font.render(pygame.font.SysFont("arial", 10), self.txt, True, (200, 200, 200))

    def update(self, d_tm):
        self.clock += d_tm
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
           if pygame.mouse.get_pressed()[0] and self.clock > self.delay:
               self.clock = 0.0
               return True

    def draw(self, screen):
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (70, 70, 70), (self.x_cord, self.y_cord , self.width, self.height))
        else:
            pygame.draw.rect(screen, (30, 30, 30), (self.x_cord, self.y_cord , self.width, self.height))

        screen.blit(self.label_text, (self.x_cord + 5 , self.y_cord + 10))

class Button_Pic:
    def __init__(self, x_cord, y_cord, file_name):

        self.clock = 0
        self.x_cord = x_cord
        self.y_cord = y_cord

        self.delay = 0.2
        self.button_image = pygame.image.load(f"{file_name}.png")
        try:
            self.button_image_on = pygame.image.load(f"{file_name}_covered.png")
        except FileNotFoundError:
            self.button_image_on = pygame.image.load(f"{file_name}.png")

        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.button_image.get_width(), self.button_image.get_height())

    def update(self, delta):
        self.clock += delta
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
           if pygame.mouse.get_pressed()[0] and self.clock > self.delay:
               self.clock = 0.0
               return True

    def draw(self, window):
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
            window.blit(self.button_image_on, (self.x_cord, self.y_cord))
        else:
            window.blit(self.button_image, (self.x_cord, self.y_cord))

class Checker_once:
    def __init__(self, x_cord, y_cord, state=False):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.field_image_false = pygame.image.load("graph/menu/checkbox_false.png")
        self.field_image_true = pygame.image.load("graph/menu/checkbox_true.png")
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.field_image_false.get_width(), self.field_image_false.get_height())
        self.field_state = state
        self.clock = 0

    def tick(self, delta):
        self.clock += delta
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] and self.clock > 0.1:
                self.field_state = not self.field_state
                self.clock = 0

        return self.field_state

    def draw(self, window):
        if self.field_state:
            window.blit(self.field_image_true, (self.x_cord, self.y_cord))
        else:
            window.blit(self.field_image_false, (self.x_cord, self.y_cord))

    def draw_text(self, window, text, r, g, b):
        text_field = pygame.font.Font.render(pygame.font.SysFont("arial", 16), f"{text}", True, (r, g, b))
        window.blit(text_field, (self.x_cord + 40, self.y_cord + 7))

class Choose_Continu:
    def __init__(self, x_cord_R, y_cord_R, x_cord_L, y_cord_L, list, start=0):
        self.button_R = Button(x_cord_R, y_cord_R, 'graph/arrow_right')
        self.button_L = Button(x_cord_L, y_cord_L, 'graph/arrow_left')
        self.lenght = len(list)
        self.iterator = start
        self.clock = 0
        self.val = 0

    def tick(self, delta):
        if self.iterator < self.lenght:
            self.val = self.iterator
        if self.button_R.tick(delta):
            if self.iterator >= self.lenght - 1:
                self.iterator = 0
            else:
                self.iterator += 1
            self.clock = 0
        if self.button_L.tick(delta):
            if self.iterator <= 0:
                self.iterator = self.lenght - 1
            else:
                self.iterator -= 1
            self.clock = 0

        return self.val

    def draw(self, window):
        self.button_R.draw(window)
        self.button_L.draw(window)


