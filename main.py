from lib.gopherpysat import Gophersat
from lib.wumpus03 import *
from math import *
import time
from lib.wumpus_client4 import *
from pprint import pprint
from requests.exceptions import HTTPError


gophersat_exec ="./lib/gophersat-1.1.6"



def Def_variable(Taille_jeu) :
    #Liste de toutes les variables
    #Utilisation d'un dictionnaire pour une raison de lisibilité
    V = {} 
    for i in range(1,Taille_jeu+1,1):
        for j in range(1,Taille_jeu+1,1):

            #Pour chaque case on initialise une variable "Brise"
            V["B"+str(i)+"|"+str(j)]= 'BP'+str(i)+"|"+str(j)
            #Pour chaque case on initialise une variable "Fosse"
            V["F"+str(i)+"|"+str(j)]= 'FP'+str(i)+"|"+str(j)
            #Pour chaque case on initialise une variable "Gold"
            V["G"+str(i)+"|"+str(j)]= 'GP'+str(i)+"|"+str(j)      
            #Pour chaque case on initialise une variable "Puit"       
            V["P"+str(i)+"|"+str(j)]= 'PP'+str(i)+"|"+str(j)
            #Pour chaque case on initialise une variable "Wumpus"
            V["W"+str(i)+"|"+str(j)]= 'WP'+str(i)+"|"+str(j)

    return V

def Clause_jeu_wumpus(V,Taille_jeu):

    C=[] #Liste de toutes les clauses
    C.append("-WP1|1") #Pas de Wumpus sur la case (1,1)
    C.append("-PP1|1") #Pas de puit sur la case (1,1)
    C.append("-FP1|1,WP1|2,WP2|1")
    C.append("-BP1|1,PP1|2,PP2|1")
    clauseFet = ""
    clauseWump = ""
    clauseBrise = ""
    clausePuit = ""
    wumpusExiste = ""
    goldExiste = ""
    posImpossible = []
    
    #for k in range(1,(17-1)):#Pas de Wumpus pour W11 Donc 17-1 Clause
    for k in range(1,Taille_jeu*Taille_jeu):

        compteur = 1
        wumpusExistePas = []
        goldExistePas = [] 
        posX = 0
        posY = 0
        PosXFet1 = 0
        PosYFet1 = 0
        PosXFet2 = 0
        PosYFet2 = 0
        PosXFet3 = 0
        PosYFet3 = 0
        PosXFet4 = 0
        PosYFet4 = 0

        for i in range(1,Taille_jeu+1,1):

            for j in range(1,Taille_jeu+1,1):
                
                if (j!= 1 or i !=1):#On ne traite pas la case (1,1) car on peut pas avoir de Wumpus ici
                    
                    if(k==1):#Uniquement lors de la première ittération de la boucle k, car on veut écrire qu'une seule fois la clause
                        if (len(wumpusExiste) != 0):
                            wumpusExiste += ","
                        if (len(goldExiste) != 0):
                            goldExiste += ","
                        wumpusExiste += V["W"+str(i)+"|"+str(j)]
                        goldExiste += V["G"+str(i)+"|"+str(j)]
                
                    #A cette étape, on sait qu'on est passé  exactement 1 fois par chaque case
                    #Donc on écrit la clause k==1 permet de s'assurer qu'on l'écrit une seule fois
                    if(k==1 and j==Taille_jeu and i==Taille_jeu):
                        C.append(wumpusExiste)
                        C.append(goldExiste)

                    #On suppose que le wumpus et l'or se situe sur la kème case en position (x,y)
                    if ( compteur == k ):
                        posX = i
                        posY = j

                    #Le wumpus et l'or ne se situe pas ici
                    #on enfile donc les positions dans une file pour les traiter plus tard
                    else:
                        posImpossible.append(str(i)+"|"+str(j))
                    
                    compteur+= 1

        #Les positions impossible pour le wumpus sachant sa position (x,y)
        while (len(posImpossible) != 0):
            C.append("-"+V["W"+str(posX)+"|"+str(posY)]+",-"+V["W"+posImpossible[0]])
            posImpossible.pop(0)   
        
        #Vérification des coordonées possibles pour la brise et l'odeur fétide
        #en supposant les coordonnées du puit et du wumpus (x,y)
        if (posX+1 <= Taille_jeu):
            PosXFet1 = posX+1
        if (posX-1 >= 1):
            PosXFet2 = posX-1
        if (posY+1 <= Taille_jeu):
            PosYFet3 = posY+1
        if (posY-1 >= 1):
            PosYFet4 = posY-1

        PosYFet1 = posY
        PosYFet2 = posY
        PosXFet3 = posX
        PosXFet4 = posX
        
        #Ecriture des clauses pour l'odeur Fetide et la brise
        clauseFet   = "-"+V["F"+str(posX)+"|"+str(posY)]
        clauseBrise = "-"+V["B"+str(posX)+"|"+str(posY)]
        clauseWump  = "-"+V["W"+str(posX)+"|"+str(posY)]
        clausePuit  = "-"+V["P"+str(posX)+"|"+str(posY)]

        if (PosXFet1 != 0 ): #Si La brise ou l'odeur fétide est en dehors de la case on ne fait rien
            #Si il y a de la brise il peut y avoir un wumpus dans les cases adjacentes
            clauseFet = clauseFet + ","+V["W"+str(PosXFet1)+"|"+str(PosYFet1)]
            #Si il y a une brise il peut y avoir un puit dans les cases adjacentes
            clauseBrise = clauseBrise + ","+V["P"+str(PosXFet1)+"|"+str(PosYFet1)]
            #Autour du wumpus il y a forcément une odeur fétide
            C.append(clauseWump + ","+V["F"+str(PosXFet1)+"|"+str(PosYFet1)])
            # Autour du puit il y a forcément une brise
            C.append(clausePuit + ","+V["B"+str(PosXFet1)+"|"+str(PosYFet1)])

        if (PosXFet2 != 0):
            clauseFet = clauseFet + ","+V["W"+str(PosXFet2)+"|"+str(PosYFet2)]
            clauseBrise = clauseBrise + ","+V["P"+str(PosXFet2)+"|"+str(PosYFet2)]
            C.append(clauseWump + ","+V["F"+str(PosXFet2)+"|"+str(PosYFet2)])
            C.append(clausePuit + ","+V["B"+str(PosXFet2)+"|"+str(PosYFet2)])

        if (PosYFet3 != 0):
            clauseFet = clauseFet + ","+V["W"+str(PosXFet3)+"|"+str(PosYFet3)]
            clauseBrise = clauseBrise + ","+V["P"+str(PosXFet3)+"|"+str(PosYFet3)]
            C.append(clauseWump + ","+V["F"+str(PosXFet3)+"|"+str(PosYFet3)])
            C.append(clausePuit + ","+V["B"+str(PosXFet3)+"|"+str(PosYFet3)])

        if (PosYFet4 != 0):
            clauseFet = clauseFet + ","+V["W"+str(PosXFet4)+"|"+str(PosYFet4)]
            clauseBrise = clauseBrise + ","+V["P"+str(PosXFet4)+"|"+str(PosYFet4)]
            C.append(clauseWump + ","+V["F"+str(PosXFet4)+"|"+str(PosYFet4)])
            C.append(clausePuit + ","+V["B"+str(PosXFet4)+"|"+str(PosYFet4)])

        #On ajoute les clauses obtenues à la liste de clause
        C.append(clauseFet)
        C.append(clauseBrise)

    return C

def Test_gophersat(V, C, mesClausesATester,Gopher_Voc,Gopher_Clause):

    if (len(Gopher_Voc) == 0):
        #Mis en forme du vocabulaire sous forme de tableau
        for variable in V.values():
            Gopher_Voc.append(variable)

    gs = Gophersat(gophersat_exec, Gopher_Voc)

    #Ajout des clauses supplémentaire apporter par l'exploration de la carte
    for i in range(len(mesClausesATester)):
        C.append(mesClausesATester[i])


    #Traitement du tableau de clause
    #On réecrit les clauses afin qu'elles puissent être interprétées par les différentes méthodes de gopherpysat
    for element in C:
        posVirgule = 0
        oldPosVirgule = 0
        debut = 0
        gopherClause = []

        #On relève la position de la virgule tant qu'il y a une virgule à lire
        while (posVirgule != (-1)):
            posVirgule = element.find(',',debut,len(element))
            if (posVirgule != -1):
                #print(element[debut:posVirgule])
                #On écrit jusqu'a la première virgule
                gopherClause.append(element[debut:posVirgule])
            else:
                #print(element[oldPosVirgule+1:len(element)]) #Le dernier ne s'affiche pas correctement car plus de virgule
                #S'il n'y a plus de virgule alors on écrit de la position connu jusqu'a la fin de la clause
                if (oldPosVirgule != 0):
                    gopherClause.append(element[oldPosVirgule+1:len(element)])
                #Si il n'y a pas de virgule alors, on écrit toute la clause
                else:
                    gopherClause.append(element)
            debut = posVirgule +1
            oldPosVirgule = posVirgule   
        Gopher_Clause.append(gopherClause)
        
    #Ecriture de la clause avec la méthode push_pretty_clause et les clauses formatées
    for i in Gopher_Clause:
        gs.push_pretty_clause(i)

    for i in range(len(mesClausesATester)):#Je sais pas comment ne pas modifier la variable globale C (qui est sensé être locale)
        Gopher_Clause.pop(-1)
    
    C.clear()
    return gs.solve()

def cartographie (V, C, world,Taille_jeu,Gopher_Voc,Gopher_Clause,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY):


    aRetesterX = []
    aRetesterY = []
    nombreIter = 0
    limiteIter = 2

    for i in range(1,Taille_jeu+1,1): 
        for j in range(1,Taille_jeu+1,1):
            nombreIter += 1
            if ( nombreIter < limiteIter and (i == 1  and j == 1 ) or (Test_gophersat(V,C,['WP'+str(i)+"|"+str(j)+","+'PP'+str(i)+"|"+str(j)],Gopher_Voc,Gopher_Clause) == False )):#and Test_gophersat(V,C,['PP'+str(i)+"|"+str(j)],Gopher_Voc,Gopher_Clause) == False  )):
                #print("Probe à 10 ici !")
                probing(i,j,world,C,False,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY)
                nombreIter = 0
            else:
                aRetesterX.append(i)
                aRetesterY.append(j)

    while (len(aRetesterX) != 0):
        nombreIter = 0
        deduction = False
        probeA10 = False

        if ( True ): #deduction == False
            for i in range(-1,-len(aRetesterX)-1,-1):
                nombreIter += 1
                if (nombreIter < limiteIter and Test_gophersat(V,C,['WP'+str(aRetesterX[i])+"|"+str(aRetesterY[i])+","+'PP'+str(aRetesterX[i])+"|"+str(aRetesterY[i])],Gopher_Voc,Gopher_Clause) == False): # and Test_gophersat(V,C,['PP'+str(aRetesterX[i])+"|"+str(aRetesterY[i])],Gopher_Voc,Gopher_Clause) == False ):
                    probing(aRetesterX[i],aRetesterY[i],world,C ,False,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY)
                    #print("Probe 10")
                    nombreIter = 0
                    aRetesterX.pop(i)
                    aRetesterY.pop(i)
                    probeA10 = True
                    break
            if (len(aRetesterX) != 0 and probeA10 == False):
                probing(aRetesterX[-1],aRetesterY[-1],world,C,True,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY)
                #print("Probe 50")
                aRetesterX.pop(-1)
                aRetesterY.pop(-1)                    


    return
            
def probing (posX, posY, world, C, Cautious,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY):

    if (Cautious == False):
        caseValeur = world.probe(int(posX)-1,int(posY)-1)
    else:
        caseValeur= world.cautious_probe(posX-1,posY-1)


    triggerB = False
    triggerG = False
    triggerS = False
    triggerP = False
    triggerW = False
    triggerRien = False

    for i in caseValeur[1]:

        if i == ".":
            C.append("-BP"+str(posX)+"|"+str(posY))
            C.append("-PP"+str(posX)+"|"+str(posY))
            C.append("-FP"+str(posX)+"|"+str(posY))
            C.append("-GP"+str(posX)+"|"+str(posY))
            C.append("-WP"+str(posX)+"|"+str(posY))
            triggerRien = True
        elif i == "B":
            C.append("BP"+str(posX)+"|"+str(posY))
            triggerB = True
        elif i == "G":
            C.append("GP"+str(posX)+"|"+str(posY))
            PosGoldX.append(str(posX))
            PosGoldY.append(str(posY))
            triggerG = True
        elif i == "S":
            C.append("FP"+str(posX)+"|"+str(posY))
            triggerS = True
        elif i == "P":
            C.append("PP"+str(posX)+"|"+str(posY))
            PosInterditeX.append(str(posX))
            PosInterditeY.append(str(posY))
            triggerP = True
        elif i == "W":
            C.append("WP"+str(posX)+"|"+str(posY))
            PosInterditeX.append(str(posX))
            PosInterditeY.append(str(posY))
            triggerW = True
        else:
            print("Sondage inutile et cher...",posX,posY,caseValeur[1])
            probing(posX,posY,world,C,True,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY)
            return

    if triggerRien == False:
        if triggerB == False:
            C.append("-BP"+str(posX)+"|"+str(posY))
        if triggerG == False:
            C.append("-GP"+str(posX)+"|"+str(posY))
        if triggerS == False:
            C.append("-FP"+str(posX)+"|"+str(posY))
        if triggerP == False:
            C.append("-PP"+str(posX)+"|"+str(posY))
        if triggerW == False:
            C.append("-WP"+str(posX)+"|"+str(posY))       

def chemin (world, V, C, PosGoldX,PosGoldY,Taille_jeu, PosInterditeX, PosInterditeY):

    graphe = []
    coordonneesDeplacementX = []
    coordonneesDeplacementY = [] 
    Dlambda =[]
    visite = []
    P = []
    nombreVisite = 0
    posInterdite = 0
    posXAdj = 0
    coordX = 0

    #Retour en (0,0)
    PosGoldX.append(1)
    PosGoldY.append(1)

    for i in range(Taille_jeu*Taille_jeu):
        graphe.append([])
        P.append(int(-1))
        visite.append("Faux")
        Dlambda.append(10000)

        if (i%Taille_jeu == 0):
            coordX = (i//Taille_jeu + 1)
        else:
            coordX = (ceil(i /Taille_jeu))
        
        for j in range(Taille_jeu*Taille_jeu):
            graphe[i].append(0)

            if (j%Taille_jeu == 0):
                    posXAdj = (j//Taille_jeu + 1)
            else:
                posXAdj = (ceil(j /Taille_jeu))
            
            if ( (j == i+1 and posXAdj == coordX ) or j == i+Taille_jeu or (j == i-1 and posXAdj == coordX ) or j == i-Taille_jeu ):
                graphe[i][j] = 1 


    for i in range(len(PosInterditeX)):
        posInterdite = (int(PosInterditeX[i])*Taille_jeu)-Taille_jeu + int(PosInterditeY[i]) -1
        for z in graphe:
            z[posInterdite] = 0

    for nombreGold in range(len(PosGoldX)):        

        if (nombreGold != 0):
            for i in range(Taille_jeu*Taille_jeu):                
                P[i] = int(-1)
                Dlambda[i] = 10000
                visite[i] = "Faux"
            Dlambda[positionCourante] = 0
            P[positionCourante] = positionCourante
        else:
            Dlambda[0] = 0
            P[0] = 0
            positionCourante = 0

        DposGold = (int(PosGoldX[nombreGold])*Taille_jeu)-Taille_jeu + int(PosGoldY[nombreGold]) -1
        nombreVisite = 0

        #Algorithme de Djikstra
        while (nombreVisite < Taille_jeu*Taille_jeu):
            minimumDjikstra = int(-1)
            for i in range(Taille_jeu*Taille_jeu):
                if (visite[i] == "Faux" and minimumDjikstra == -1 ):  
                    minimumDjikstra = i 
                elif (minimumDjikstra != -1):
                    if ( visite[i] == "Faux" and (Dlambda[i] < Dlambda[minimumDjikstra] ) ):
                        minimumDjikstra = i  

            visite[minimumDjikstra] = "Vrai"
            nombreVisite+= 1
        

            for z in range(Taille_jeu*Taille_jeu):
                if (graphe[minimumDjikstra][z] == 1):
                    if (visite[z] == "Faux" and Dlambda[z] > Dlambda[minimumDjikstra] + 1):
                        Dlambda[z] = Dlambda[minimumDjikstra] +1
                        P[z] = minimumDjikstra 
        

        #Si il existe un chemin jusqu'a l'or on l'affiche
        if (Dlambda[DposGold] != 10000 and P[DposGold] != -1):
            positionCourante = DposGold
            coordonneesDeplacementX.append(int(PosGoldX[nombreGold]))
            coordonneesDeplacementY.append(int(PosGoldY[nombreGold]))
            deplacementCase = P[DposGold]
            for i in range(Dlambda[DposGold]-1):
                if (deplacementCase%Taille_jeu == 0):
                    coordonneesDeplacementX.append(deplacementCase//Taille_jeu + 1)
                else:
                    coordonneesDeplacementX.append(ceil(deplacementCase /Taille_jeu)) #Arrondi entier supérieur

                coordonneesDeplacementY.append(deplacementCase%Taille_jeu + 1)

                deplacementCase = P[deplacementCase]
            coordonneesDeplacementX.append(int(-1))
            coordonneesDeplacementY.append(int(-1))
        else:
            if (len(PosGoldX) == nombreGold):
                return coordonneesDeplacementX,coordonneesDeplacementY

    return coordonneesDeplacementX,coordonneesDeplacementY

def parcours_chemin(posX,posY,world):

    posX.reverse()
    posY.reverse()
    pileX = []
    pileY = []
    taille_chemin = len(posX)
    suiteCaseX =[]
    suiteCaseY =[]
        
    while(len(posX) != 0):
        
        if (posX[-1] != -1):
            pileX.append(posX[-1])
            pileY.append(posY[-1])
            posX.pop(-1)
            posY.pop(-1)
        else:
            posX.pop(-1)
            posY.pop(-1)

            for j in range(-1,-len(pileX)-1,-1):
                suiteCaseX.append(int(pileX[j]-1))
                suiteCaseY.append(int(pileY[j]-1))
            pileX.clear()
            pileY.clear()         

    print("Déplacement en X",suiteCaseX)
    print("Déplacement en Y",suiteCaseY)
    
    for i in range(len(suiteCaseX)):
        if (world.get_position()[0] != suiteCaseX[i] or world.get_position()[1] != suiteCaseY[i] ):
            world.go_to(suiteCaseX[i],suiteCaseY[i])
    #Local
    #return suiteCaseX,suiteCaseY

def Intelligence_artificielle_lol(world,size,Remote):

    start_time=time.time() #taking current time as starting time

    Taille_jeu = size
    PosGoldX = []
    PosGoldY = []
    PosInterditeX = []
    PosInterditeY = []
    Gopher_Voc = []
    Gopher_Clause = []

    print("Taille du jeu",Taille_jeu)
    Mes_variables = Def_variable(Taille_jeu)
    Mes_clauses = Clause_jeu_wumpus (Mes_variables,Taille_jeu)
    cartographie(Mes_variables, Mes_clauses, world,Taille_jeu,Gopher_Voc,Gopher_Clause,PosInterditeX,PosInterditeY,PosGoldX,PosGoldY)

    if Remote :
        status, msg = world.end_map()
        print(status,msg,"\n")


    print("Il y a ",len(PosGoldX)," gold à trouver\n")
    Plannification = chemin(world,Mes_variables,Mes_clauses,PosGoldX,PosGoldY,Taille_jeu,PosInterditeX,PosInterditeY)
    Parcours = parcours_chemin(Plannification[0],Plannification[1],world)
    
    
    if not(Remote) :
        print(world.get_cost())
        print("\n",world)
    

 
    if Remote :
        res = world.maze_completed()
        print(res)


    print("\n")

    elapsed_time=time.time()-start_time #again taking current time - starting time 

    print(elapsed_time)


    print("\n===========================\n")

def main(Remote):

    if Remote :
        # Remote - Connexion au server
        server = "http://lagrue.ninja"
        groupe_id = "PRJ13"  # votre vrai numéro de groupe
        names = "Maxime Partout et Dylan Cornelie"  # vos prénoms et noms

        try:
            ww = WumpusWorldRemote(server, groupe_id, names)
        except HTTPError as e:
            print(e)
            print("Try to close the server (Ctrl-C in terminal) and restart it")
            exit("Echec de connexion")

        while(True):
            #Remote
            status, msg, size = ww.next_maze()
            taille = size
            Intelligence_artificielle_lol(ww,taille,True)

    if not(Remote):
        #Local
        ww = WumpusWorld()
        taille = ww.get_n()
        Intelligence_artificielle_lol(ww,taille,False)


main(False)