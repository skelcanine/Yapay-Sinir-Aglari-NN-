import pygame
import random
import os
import time
import neat
import visualize
import pickle
pygame.font.init()  

WIN_WIDTH = 1366
WIN_HEIGHT = 768
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("11160000053")

pipe_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha(),(200,520))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (1600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,7)]
base_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha(),(900,100))

gen = 0

class Bird:
    
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        
        self.vel = -11
        self.tick_count = 0
        self.height = self.y

    def move(self):
        
        self.tick_count += 1

        
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  

        
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

    def draw(self, win):
        
        
        
        
        if gen==1:
            self.img = self.IMGS[1]
        if gen==2:
            self.img = self.IMGS[2]
        if gen==3:
            self.img = self.IMGS[3] 
        if gen==4:
            self.img = self.IMGS[0]
        if gen==5:
            self.img = self.IMGS[4]
        if gen==6:
            self.img = self.IMGS[5]
        
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
       
        return pygame.mask.from_surface(self.img)


class Pipe():

    GAP = 190
    VEL = 5

    def __init__(self, x):
        
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        
        self.height = random.randrange(30, 480)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        
        self.x -= self.VEL

    def draw(self, win):
        
        win.blit(self.PIPE_TOP, (self.x, self.top))
        
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:

    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img
    x3c = 0

    def __init__(self, y):
        
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.x3 = 2*self.WIDTH

    def move(self):
        
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        self.x3 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
            self.x3c += 1

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
            
        if self.x3c % 2 ==0:
            if self.x3<self.WIDTH:
                self.x3= self.x2+self.WIDTH-200
        if self.x3c % 2 ==0:
            if self.x3<self.WIDTH:
                self.x3= self.x1+self.WIDTH-200
                
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        win.blit(self.IMG, (self.x3, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        
        bird.draw(win)

    
    score_label = STAT_FONT.render("Skor: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    
    score_label = STAT_FONT.render("Gen: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    
    score_label = STAT_FONT.render("Canlı: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    
    global WIN, gen
    win = WIN
    gen += 1

    
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  
                pipe_ind = 1                                                                 

        for x, bird in enumerate(birds):  
            ge[x].fitness += 0.1
            bird.move()

            
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        


def run(config_file):
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    
    p = neat.Population(config)

    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    

    
    winner = p.run(eval_genomes, 50)

    
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
