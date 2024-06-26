from typing import Any
import pygame
from Attacks import *
from math import ceil
from random import choices

class Player(pygame.sprite.Sprite):

    def __init__(self,x,y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('Sprites/Character/Base.png')
        self.image = self.get_image(self.sprite_sheet, 0, 0, 64, 64) #coordonées de début du get
        self.image.set_colorkey([0, 0, 0]) #on supprime le noir
        self.rect = self.image.get_rect()
        self.retourne = False#permet de savoir si le personnage est tourneé à gauche
        
        self.pos = [x,y] #position du joueur
        self.old_pos = self.pos.copy()
        self.hitBox = [self.rect[2],self.rect[3]]#rectangle autour du joueur  
        self.feet = pygame.Rect(0,0,self.rect.width*0.5,16) #pieds pour bordure
        
        #Statistiques de vitesse, de points de vie
        self.speed = 5 #vitesse du joueur
        self.HP = 150#point de vie du joueur
        self.maxHP = 150
        
        #Protection(item)
        self.shield = False
        self.shieldcooldownmax =  100#temps d'activité du bouclir
        self.shieldcooldown = self.shieldcooldownmax
        self.LVLED = False #Verif si on gagne un niveau pour afficher
        #barre de vie
        self.ratio = self.HP / self.maxHP#permet de faire fonctionner la barre de vie

        #expérience
        self.XP = 0
        self.coeffXP = 1.5
        self.maxXP = 10 
        self.LVL = 0
        self.totalXP = 0
        self.xpratio = self.XP / self.maxXP#POur savoir quelle image de la barre d'expérience afficher 
        self.killcount = 0
        self.maxscore = 0
        
        #statistiques d'attaque
        self.degat = 4
        self.range = 250
        self.attackDelay = 0.5
        self.fireDelay = 2
        self.zoneDelay = 2
        self.zoneRange = 150# cercle de 150 px de rayon
        self.zoneDegat = 50
        self.zoneSpeed  = 10#vitesse à laquelle la zone grossi  
        self.isZone = False# booléen ppour savoir si une attaque de zone est lancé
        self.invincibl = 1 #periode pendant laquelle
        self.p1 =""
        self.p = ""
        #Probas pour niveaux
        
        

    def newtype(self):#buff random
        types = [self.maxHP,self.speed,self.shieldcooldownmax,self.range,self.attackDelay,self.fireDelay]
        probas = [0.2,0.2,0.2,0.2,0.1,0.1]
        chosen_object = choices(types, weights=probas)[0]
        return chosen_object

    def XPmanage(self):#gestion de l'expérience
        if self.XP >= self.maxXP and self.LVL<999 :
            self.XP = self.XP - self.maxXP
            self.totalXP += self.maxXP
            self.maxXP = ceil(self.maxXP * self.coeffXP)
            self.LVL += 1 
            #Buff random
            self.LVLED = True
            buff = self.newtype()
            self.p1 = "Stats IMPROVED"
            if buff == self.maxHP:
                self.maxHP += 20 
                
                self.p1 = "LIFE IMPROVED"
                buffed = self.maxHP
            if buff == self.speed:
                self.speed += 0.2
                
                self.p1 = "SPEED IMPROVED"
                buffed =self.speed  
            if buff == self.shieldcooldownmax:
                self.shieldcooldownmax += 10
                
                self.p1 = "SHIELD + 10s"
                buffed = self.shieldcooldownmax
            if buff == self.range:
                self.range += 3
                
                self.p1 = "FIREBALL RANGE IMPROVED"
                buffed = self.range
            if buff == self.attackDelay:
                self.attackDelay -= 0.0025
                
                self.p1 = "ATTACK SPEED IMPROVED"
                buffed = self.attackDelay
            if buff == self.fireDelay:
                self.fireDelay -= 0.0025
                
                self.p1 = "FIRE SPEED IMPROVED"
                buffed = self.fireDelay
            self.p = "LVL " + str(self.LVL) + "  " + self.p1
    

    def go_left(self):
        self.pos[0] -= self.speed
        if self.retourne == False:
            self.image = pygame.transform.flip(self.image,True,False)
            self.retourne = True
    
    def go_right(self): 
        self.pos[0] += self.speed
        if self.retourne == True:
            self.image = pygame.transform.flip(self.image,True,False)
            self.retourne = False

    def go_up(self): self.pos[1] -= self.speed

    def go_down(self): self.pos[1] += self.speed

    def saveloc(self): self.old_pos = self.pos.copy()

    def invincibility(self,visible):#fonction qui permet de faire clignoter le joueur pendant qu'il est invincible apres avoir recu un coup
        if visible == True:
            visible = False
            self.image = pygame.image.load("Sprites/Character/invisible.png")
        else :
            self.image = pygame.image.load('Sprites/Character/Base.png')
            if self.retourne == True:
                self.image = pygame.transform.flip(self.image,True,False)
            visible = True
        return visible
    
    def end(self,startT,endT,vague):#Si le joueur perd de la vie, on vérifie si il a encore de la vie
        if self.HP <= 0:
            gameTime = endT - startT#On calcule le temps qu'a duré une partie
            scorefile = open("main/Score.csv","r")#On lis le fichier des scores pour trouver le meilleur
            maxscore = -1
            
            for i in scorefile:
                s = int(i.split(";")[0])
                if s >= maxscore:
                    maxscore = s
            self.maxscore = maxscore
            scorefile.close()

            scorefile = open("main/Score.csv","a")#Ensuite, on écrit les statistiques de la partie
            scorefile.write(f"{self.totalXP};{self.killcount};{gameTime};{vague};{self.LVL};\n")
            scorefile.close()
            return True
        return False

    def update(self):#actualisation de la position
        if self.HP < 0: 
            self.HP = 0
        self.xpratio = self.XP / self.maxXP
        self.ratio = self.HP / self.maxHP
        self.rect.topleft = self.pos  #position
        self.feet.midbottom = self.rect.midbottom
        if self.shield: #gestion du bouclier
            if self.shieldcooldown>0:
                self.shieldcooldown -= 1
            else:
                self.shieldcooldown = self.shieldcooldownmax
                self.shield = False

    def rollback(self):#rollback pour bordures
        self.pos = self.old_pos.copy()
        self.rect.topleft = self.old_pos  #position
        self.feet.midbottom = self.rect.midbottom


    def get_image(self, myimage, x, y, x1, y1):
        image = pygame.Surface([x1, y1]) #surface occupée sur le jeu
        image.blit(myimage, (0, 0), (x, y, x1, y1)) #Origine du crop et coordonnées de fin du crop
        return image