
# LIBRARIES

import os, contextlib, sys, math, random
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):                         # omit message from pygame
    import pygame
from pygame.locals import RESIZABLE, VIDEORESIZE
pygame.init()

# COLORS

orange=209,134,0
black=0, 0, 0
white=255,255,255
light=150,150,150
dark=50,50,50
red=255,0,0
wrongred=198,172,168
darkred=120,0,0
green=0,255,0
blue=0,0,255
lightblue=68,103,196

# SETUP

def valid(m,n):                                                                         # checks for valid input
    return m>1 and n>1 and m%2==1 and n%2==1 and math.gcd(m,n)==1

while True:                                                                             # get valid input
    print("Enter odd coprime positive integers m and n:")
    try:
        m=int(input("m: "))
        n=int(input("n: "))
        if valid(m,n):
            print("Valid input received.")
            break
        else:
            print("Invalid input:")
            if m<=0 or n<=0:
                print("- Both numbers must be positive.")
            if m==1 or n==1:
                print("- The number 1 is too small.")
            if m%2==0 or n%2==0:
                print("- Both numbers must be odd.")
            if math.gcd(m, n)!=1:
                print("- m and n must be coprime.")
            print("Please try again.\n")
    except ValueError:
        print("Invalid input: please enter integers only.\n")
        
info=pygame.display.Info()                                                              # set initial scale depending on screen size and input
w=0.65*info.current_w
h=0.65*info.current_h
scale_m = int(0.1*info.current_h)
scale_n = int(0.1*info.current_w)
if m>3 or n>7:
    scale_m=int(h/m)
    scale_n=int(w/n)
scale=min(scale_m, scale_n)
size=width, height=(n+2)*scale,(m+2)*scale

def prime(n):                                                                           # checks if a number in prime
    if n<=1:
        return False
    if n==2:
        return True
    if n%2==0:
        return False

    root=int(math.sqrt(n))+1
    for i in range(3, root, 2):
        if n%i==0:
            return False
    return True

def legendre(m,n):                                                                      # calculates legendre symbol (if the visualization is not possible)
    if n<=2 or not prime(n):
        raise ValueError("n must be an odd prime number.")
    m=m%n
    if m==0:
        return 0 # (0/n) = 0
    if m==1:
        return 1 # (1/n) = 1
    result=1
    while m!=0:
        m=m%n        
        if m%2==0: # quadratic reciprocity
            if n%8 in {3, 5}: # (2/n) depends on n mod 8
                result=-result
            m//=2
        elif m%4==3 and n%4==3: # only case where the sign flips
            result=-result
            m, n=n, m 
        else:
            m, n=n, m
    return result if n==1 else 0

quadrec=False # this controls if the number of checkers in the solution should be counted (for a bottom row puzzle)
run=True # this controls if the visualization should run

if scale<=10:                                                                           # deal with number too big for the visualization
    run=False
    if prime(n):
        print("Numbers too big for visualization, the Legendre symbol is "+str(legendre(m,n))+".")
    else:
        print("Numbers too big for visualization.")
        
if run:                                                                                 # determine if it should be a bottom row puzzle
    question=input("Pebbles only on the bottom row? (yes/no): ")
    quadrec=question.lower()=="yes" or question.lower()=="y" or question.lower()=="1"

clock=pygame.time.Clock()                                                               # set up clock and screen with (potentiallly) random puzzle
s=500
screen=pygame.display.set_mode(size, RESIZABLE)
pygame.display.set_caption("Parity Checkers with Arithmetic Billiards")
font=pygame.font.SysFont("bahnschrift",17)
dimensions=(m-1)*(n-1)
randombits=random.getrandbits(dimensions)
bitstring=f"{randombits:0{dimensions}b}"

pebbleboard = [[int(bitstring[i*(n-1)+j]) for j in range (n-1)] for i in range(m-1)]    # set up pebble positions as list of lists using random bits
for row in range(m-1):                                                                  # no checkers on black squares
    for col in range(n-1):
        if (col+row)%2!=0:
            pebbleboard[row][col]=0                                                     
if quadrec:                                                                             # set up bottom row puzzle
    for row in range(m-2):
        for col in range(n-1):
                pebbleboard[row][col]=0
    for col in range (n-1):
        if (col+m-2)%2==0:
            pebbleboard[m-2][col]=1
checkerboard=[[0 for j in range (n-1)] for i in range(m-1)]                             # set up checker positions (initially empty)
marks=[[0 for j in range (n-1)] for i in range(m-1)]                                    # marks to help with solving
paint=[False for j in range(n+1)]                                                       

def adjust_size(w, h):                                                                  # used to adjust dimensions when resizing
    rescale = max(round(min(w / (n+2), h / (m+2))),2)
    adjusted_width = rescale * (n+2)
    adjusted_height = rescale * (m+2)
    return adjusted_width, adjusted_height

ball = (scale, height-scale)                                                            # ball position and lists of bounces for trail display and calculation
t=scale
sign=1
left=[]
right=[]
top=[]
bottom=[]
show_result=True # controls if the result should be printed (which should be only once)
trail = [ball]
speed=[scale,-scale]
bluetrail = []
painted=False

def reset():                                                                            # resets the ball to the start
    global ball
    global trail
    global speed
    global t
    global left
    global right
    global top
    global bottom
    global bluetrail
    global painted
    ball=(scale, height-scale)
    trail=[ball]
    speed=[scale, -scale]
    t=scale
    left=[]
    right=[]
    top=[]
    bottom=[]
    bluetrail=[]
    painted=False
    
billiardmode=1                                                                          # variables to control the solver
calculated=False
restart=False
corner=False
modeswitch=False
autosolve=1
bottomsolve=[]
marking=2
ready=True
settingmode=False

def neighbours(i,j):                                                                    # sums up the number of checkers in the neighborhood
    if (i+j)%2!=0:
        return pebbleboard[i][j]
    if i==0:
        if j==0:
            return checkerboard[0][1]+checkerboard[1][0]
        if j==n-2:
            return checkerboard[0][n-3]+checkerboard[1][n-2]
        else:
            return checkerboard[0][j-1]+checkerboard[1][j]+checkerboard[0][j+1]
    if i==m-2:
        if j==0:
            return checkerboard[m-3][0]+checkerboard[m-2][1]
        if j==n-2:
            return checkerboard[m-3][n-2]+checkerboard[m-2][n-3]
        else:
            return checkerboard[m-2][j-1]+checkerboard[m-3][j]+checkerboard[m-2][j+1]
    if j==0:
        return checkerboard[i-1][0]+checkerboard[i][1]+checkerboard[i+1][0]
    if j==n-2:
        return checkerboard[i-1][n-2]+checkerboard[i][n-3]+checkerboard[i+1][n-2]
    else:
        return checkerboard[i-1][j]+checkerboard[i][j-1]+checkerboard[i+1][j]+checkerboard[i][j+1]
    
# MAIN LOOP    

while run:                                                                              # loop for visualization
    for event in pygame.event.get():                                                    # get input from mouse and keyboard
        
        if event.type==pygame.QUIT:                                                     # quit loop
            run=False
            
        if event.type==VIDEORESIZE:                                                     # resize window 
            width, height=adjust_size(event.w, event.h)
            scale=min(width//(n+2),height//(m+2))
            if(scale)>10:                                                               
                width, height=((2+n)*scale, (2+m)*scale)
                screen=pygame.display.set_mode((width, height), RESIZABLE)
            else:                                                                       # set a minimum size/scale
                scale=11
                width, height=((2+n)*scale, (2+m)*scale)
                screen=pygame.display.set_mode((width, height), RESIZABLE)
            reset()                                                                     # reset after resizing to avoid errors
            checkerboard=[[0 for j in range (n-1)] for i in range(m-1)]
            marks=[[0 for j in range (n-1)] for i in range(m-1)]
            paint=[False for j in range(n+1)]
            billiardmode=1
            restart=False
            corner=False
            modeswitch=False
            autosolve=1
            bottomsolve=[]
            marking=2
            ready=True
            settingmode=False
            calculated=True
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y=event.pos
            row=(y-scale//2)//scale-1
            col=(x-scale//2)//scale-1
            
            if 0<=row<(m-1) and 0<=col<(n-1) and (col+row)%2!=0:                        
                autosolve=0
                if event.button==3:                                                     # put mark on dark square (right click)
                    marks[row][col]=1-marks[row][col]
                else:
                    checkerboard[row][col]=1-checkerboard[row][col]                     # put checker on dark square (left click)
            if 0<=row<(m-1) and 0<=col<(n-1) and (col+row)%2==0 and settingmode:
                autosolve=0
                quadrec=False
                pebbleboard[row][col]=1-pebbleboard[row][col]                           # put pebble on light square (if the control variable "checkingmode" is on)

            if row==m-1 and 0<=col<(n-1) and col%2==1:
                autosolve=0
                paint[col]=not paint[col]                                               # paint square below the bottom row to color the path if it bounces there
                
            if (x<=scale and y>=height-scale):                                          # this is the ORANGE button which switches the running "modes" of the billiard, starting and stopping it
                autosolve=0
                if billiardmode==0: # if normal mode
                    billiardmode=1 # pause mode
                elif billiardmode==1: # if pause mode
                    modeswitch=False # this should only be true right after the path finishes at a corner 
                    billiardmode=0 # normal mode
                elif billiardmode==2: # if reset mode
                    billiardmode=0 #pause mode
                elif billiardmode==3: # if fast forward mode
                    billiardmode=2 # reset mode
                    
            if (x<=scale and y<=scale):                                                 # this is the RED button which fasts forward the billiard
                autosolve=0
                if modeswitch: # if the path just finished
                    billiardmode=2 # reset mode
                    modeswitch=False
                else:
                    corner=False # not at the end yet
                    billiardmode=3 # fast forward mode
                    
            if (x>=width-scale and y>=height-scale):                                    # this is the GREEN button which checks if the puzzle is solved
                solved=all(all(neighbours(i,j)%2==pebbleboard[i][j] for i in range(m-1))for j in range (n-1)) # check all parity constraints
                if not solved:
                    print("The puzzle is not solved: \nFrom the top left we have:")
                    for j in range (n-1):
                        for i in range(m-1):
                            if neighbours(i,j)%2!=pebbleboard[i][j]:
                                print("The square ("+str(i)+", "+str(j)+") has  "+str(neighbours(i,j))+" surrounding checker(s).") # print squares left to solve
                else:
                    print("The puzzle is solved.")
                    if quadrec: # if it is a bottom row puzzle and the checkers in the solution have not been counted
                        checknum=0
                        for row in range(m-1):
                            for col in range(n-1):
                                if (col+row)%2!=0:
                                    checknum+=checkerboard[row][col]
                        print("There are "+str(checknum)+" checkers in the solution, so the (generalized) Legendre symbol is (-1)^"+str(checknum)+"=" + str((-1)**checknum)+".") # print legendre symbol calculated with the number of checkers in the solution
                        quadrec=False
                        
            if (x>=width-scale and y<=scale):                                           # this is the BLUE button which solves the puzzle using the algorithm
                
                if autosolve==2 and not settingmode:                                    # this solve mode does the coloring part of the algorithm
                    if marking==2:
                        if len(bottomsolve)==0:                                         # if the puzzle is solved, print message and possibly calculate legendre symbol based on number of checkers 
                            print("The puzzle is solved.")
                            if quadrec:
                                checknum=0
                                for row in range(m-1):
                                    for col in range(n-1):
                                        if (col+row)%2!=0:
                                            checknum+=checkerboard[row][col]
                                print("There are "+str(checknum)+" checkers in the solution, so the (generalized) Legendre symbol is (-1)^"+str(checknum)+"="+ str((-1)**checknum)+".")
                                quadrec=False
                        else:                                                           # otherwise, choose the first wrong square, paint the square below blue and fast forward the ball 
                            newblue=bottomsolve.pop(0)
                            paint[newblue]=True
                            reset()
                            corner=False
                            billiardmode=3 # fast forward mode
                            marking=0 # next, marks on different-color intersections will be placed
                            ready=False # not ready for instant placement of the marks, wait for visualization
                    if marking==1:                                                      # place or remove checkers at the marked squares
                        for row in range(m-1):
                            for col in range(n-1):
                                if marks[row][col]==1:
                                    checkerboard[row][col]=1-checkerboard[row][col]
                                    marks[row][col]=0
                        marking=2
                        paint[newblue]=False
                        billiardmode=2
                    if marking==0 and ready and len(bottom)>0:
                        for row in range(m-1):
                            for col in range(n-1):
                                if row+col%2!=0:                                        # calculate different-color intersection points bssed on the bounces saved in the lists for the trail and the blue part of the trail
                                    if next((p for p in bottom if p[1]==(newblue+2)*scale),None)[0]>0:
                                        endbluetrail=bluetrail
                                        endbluetrail.append(ball)
                                        if any(((1+col-row)*scale, scale)==point for point in trail)or any(((m+1+col-row)*scale,height-scale)==point for point in trail)or any((scale, (1+row-col)*scale)==point for point in trail):
                                            if any(((3+row+col)*scale, scale)==point for point in endbluetrail)or any(((-m+3+col+row)*scale,height-scale)==point for point in endbluetrail)or any((scale,(row+col+3)*scale)==point for point in endbluetrail):
                                                marks[row][col]=1 # mark intersection point
                                        newbluetrail=bluetrail[1:] # remove paint point
                                        newbluetrail.append(ball)
                                        newtrail=trail[:-1]
                                        if any(((3+row+col)*scale, scale)==point for point in newtrail)or any(((-m+3+col+row)*scale,height-scale)==point for point in newtrail) or any((scale,(row+col+3)*scale)==point for point in newtrail):
                                            if any(((1+col-row)*scale, scale)==point for point in newbluetrail)or any(((m+1+col-row)*scale,height-scale)==point for point in newbluetrail)or any((scale, (1+row-col)*scale)==point for point in newbluetrail):
                                                marks[row][col]=1 # mark intersection point
                                    if next((p for p in bottom if p[1]==(newblue+2)*scale),None)[0]<0:
                                        endbluetrail=bluetrail
                                        endbluetrail.append(ball)
                                        if any(((3+row+col)*scale, scale)==point for point in trail)or any(((-m+3+col+row)*scale,height-scale)==point for point in trail)or any((scale,(row+col+3)*scale)==point for point in trail):
                                            if any(((1+col-row)*scale, scale)==point for point in endbluetrail)or any(((m+1+col-row)*scale,height-scale)==point for point in endbluetrail)or any((scale, (1+row-col)*scale)==point for point in endbluetrail):
                                                marks[row][col]=1 # mark intersection point
                                        newbluetrail=bluetrail[1:] # remove paint point
                                        newtrail=trail[:-1]
                                        if any(((1+col-row)*scale, scale)==point for point in newtrail)or any(((m+1+col-row)*scale,height-scale)==point for point in newtrail)or any((scale, (1+row-col)*scale)==point for point in newtrail):
                                            if any(((3+row+col)*scale, scale)==point for point in newbluetrail)or any(((-m+3+col+row)*scale,height-scale)==point for point in newbluetrail)or any((scale,(row+col+3)*scale)==point for point in newbluetrail):
                                                marks[row][col]=1 # mark intersection point             
                        marking=1 # next, checkers will be placed or removed from the marked squares
                    ready=True # ready for placement of the marks at the next click
                    
                if autosolve==1 and not settingmode:                                    # this solve mode does the first, simple part of the algorithm ("chase the lights")
                    billiardmode=2
                    for i in range(m-2):
                        for j in range (n-1):
                            if neighbours(i,j)%2!=pebbleboard[i][j]:
                                checkerboard[i+1][j]=1
                    bottomsolve=[]
                    for j in range (n-1):
                            if neighbours(m-2,j)%2!=pebbleboard[m-2][j]:
                                bottomsolve.append(j)
                    autosolve=2
                    
                if autosolve==0 and not settingmode:                                    # this solve mode clears the board before beginning to solve it
                    billiardmode=2
                    checkerboard=[[0 for j in range (n-1)] for i in range(m-1)]
                    marks=[[0 for j in range (n-1)] for i in range(m-1)]
                    paint=[False for j in range(n+1)]
                    bottomsolve=[]
                    autosolve=1
                    
        if event.type==pygame.KEYDOWN:
            
            if event.key==pygame.K_SPACE:                                               # set new puzzle using random bits                                             
                quadrec=False
                autosolve=1
                bottomsolve=[]
                marking=2
                randombits=random.getrandbits(dimensions)
                bitstring=f"{randombits:0{dimensions}b}"
                pebbleboard=[[int(bitstring[i*(n-1)+j]) for j in range (n-1)] for i in range(m-1)]
                for row in range(m-1):
                    for col in range(n-1):
                        if (col+row)%2!=0:
                            pebbleboard[row][col]=0
                checkerboard=[[0 for j in range (n-1)] for i in range(m-1)]
                marks=[[0 for j in range (n-1)] for i in range(m-1)]
                paint=[False for j in range(n+1)]
                modeswitch=False
                billiardmode=2 # reset mode
                
            if event.key==pygame.K_s:                                                   # reset to avoid errors and switch settingmode to allow or disallow setting pebbles
                reset()
                checkerboard=[[0 for j in range (n-1)] for i in range(m-1)]
                marks=[[0 for j in range (n-1)] for i in range(m-1)]
                paint=[False for j in range(n+1)]
                billiardmode=1
                restart=False
                corner=False
                modeswitch=False
                autosolve=1
                bottomsolve=[]
                marking=2
                ready=True
                calculated=True
                settingmode=not settingmode
                
    if billiardmode==0:                                                                 # normal running mode of the billiard
        calculated=False
        if restart:
            ball=(scale, height-scale)
            trail=[ball]
            speed=[scale,-scale]       
            t=scale
            left=[]
            right=[]
            top=[]
            bottom=[]
            bluetrail=[]
            painted=False
        restart=False
        ball=(ball[0]+abs(speed[0])//speed[0], ball[1]+abs(speed[1])//speed[1])
        if ball[1]==scale or ball[1]==height-scale:
            if painted:
                bluetrail.append(ball)
            else:
                trail.append(ball)
            speed[1]=-speed[1]
            if speed[0]>0:
                sign=1
            else:
                sign=-1
            if ball[1]==scale:
                top.append((sign*(ball[0]//scale-1),ball[0]))
            else:
                bottom.append((sign*(ball[0]//scale-1),ball[0]))
                if paint[max(ball[0]//scale-2,0)]:
                    bluetrail.append(ball)
                    painted=True
        elif ball[0]==scale or ball[0]==width-scale:
            if painted:
                bluetrail.append(ball)
            else:
                trail.append(ball)
            speed[0]=-speed[0]
            if speed[1]<0:
                sign=1
            else:
                sign=-1
            if ball[0]==scale:
                left.append((sign*((height-ball[1])//scale-1),ball[1]))
            else:
                right.append((sign*((height-ball[1])//scale-1),ball[1]))             
        if (ball[0]==scale or ball[0]==width-scale) and (ball[1]==scale or ball[1]==height-scale):
            f=1
            for a in range (0,len(bottom)):
                f=f*bottom[a][0]
            if not (ball[0]==scale and ball[1]==height-scale):
                calculated=True
                modeswitch=True
                restart=True
                billiardmode=1
                if show_result:
                    print("Product of the labels along the bottom: "+str(f))
                    print("Therefore the (generalized) Legendre symbol is "+str(f//abs(f))+" (only the sign matters)"+".")
                    show_result=False
        t=t+1
        
    if billiardmode==1:                                                                 # pause/hold mode of the billiard 
        calculated=True
        
    if billiardmode==2:                                                                 # reset mode of the billiard (not a permanent state)
        reset()
        calculated=True
        billiardmode=1
        modeswitch=False
        
    if billiardmode==3:                                                                 # fast forward mode of the billiard (not a permanent state)
        restart=True
        while not corner:                                                               # loop over the running mode of the billiard until a corner is met
            ball=(ball[0]+abs(speed[0])//speed[0], ball[1]+abs(speed[1])//speed[1])
            if ball[1]==scale or ball[1]==height-scale:
                if painted:
                    bluetrail.append(ball)
                else:
                    trail.append(ball)
                speed[1]=-speed[1]
                if speed[0]>0:
                    sign=1
                else:
                    sign=-1
                if ball[1]==scale:
                    top.append((sign*(ball[0]//scale-1),ball[0]))
                else:
                    bottom.append((sign*(ball[0]//scale-1),ball[0]))
                    if paint[max(ball[0]//scale-2,0)]:
                        bluetrail.append(ball)
                        painted=True
            elif ball[0]==scale or ball[0]==width-scale:
                if painted:
                    bluetrail.append(ball)
                else:
                    trail.append(ball)
                speed[0]=-speed[0]
                if speed[1]<0:
                    sign=1
                else:
                    sign=-1
                if ball[0]==scale:
                    left.append((sign*((height-ball[1])//scale-1),ball[1]))
                else:
                    right.append((sign*((height-ball[1])//scale-1),ball[1]))             
            if (ball[0] == scale or ball[0] == width-scale) and (ball[1] == scale or ball[1] == height-scale):
                f=1
                for a in range (0,len(bottom)):
                    f=f*bottom[a][0]
                if show_result and not (ball[0] == scale and ball[1] == height-scale):
                    print("Product of the labels along the bottom: "+str(f))
                    print("Therefore the (generalized) Legendre symbol is "+str(f//abs(f))+" (only the sign matters)"+".")
                    show_result=False
                corner=True
            t=t+1
        calculated=True
        modeswitch=True
        billiardmode=1
        
    screen.fill(black) # black background
    for row in range(m-1):                                                              # draw checkerboard                                                     
        for col in range(n-1):
            if (col+row)%2==0:
                color=light
            else:
                color=dark
                pebbleboard[row][col]=0
            pygame.draw.rect(screen,color, (scale//2+(col+1)*scale, scale//2+(row+1)*scale, scale, scale))

    for col in bottomsolve:                                                             # draw bottom row squares left to solve
        pygame.draw.rect(screen,wrongred, (scale//2+(col+1)*scale, scale//2+(row+1)*scale, scale, scale))
    for i in range(n-1):                                                                # draw blue paint at the bottom
        if paint[i]:
            pygame.draw.rect(screen, blue, (scale*(2+i)-scale//2, scale*(m+1)-scale//2, scale, scale//2))

    pygame.draw.rect(screen, white, (scale, scale, width-2*scale, height-2*scale), 3)   # draw lines and trails
    if settingmode:
        pygame.draw.rect(screen, darkred, (scale, scale, width-2*scale, height-2*scale), 3)
    for i in range(2,m+1):
        pygame.draw.line(screen, white, (scale,i*scale), (width-scale, i*scale))
    for j in range(2,n+1):
        pygame.draw.line(screen, white, (j*scale, scale), (j*scale, height-scale))
    if len(trail)>1:
        pygame.draw.lines(screen,green,False,trail,5)
    if painted:
        if len(bluetrail)>1:
            pygame.draw.lines(screen,lightblue,False,bluetrail,5)
        pygame.draw.line(screen, lightblue, bluetrail[-1], ball,5)
    else:
        pygame.draw.line(screen, green, trail[-1], ball,5)
        
    for row in range(m-1):                                                              # draw pebbles, checkers and marks
        for col in range(n-1):
            if (col+row)%2==0:
                color=light
            else:
                color=dark
            if pebbleboard[row][col]==1:
                pygame.draw.circle(screen, black, (scale*(2+col),scale*(2+row)), max(scale//4,1))
            if checkerboard[row][col]==1:
                pygame.draw.circle(screen, darkred, (scale*(2+col),scale*(2+row)), max(scale//2,1))
                pygame.draw.circle(screen, red, (scale*(2+col),scale*(2+row)), max(scale//3,1))
            if marks[row][col]==1:
                pygame.draw.circle(screen, white, (scale*(2+col),scale*(2+row)), max(scale//4,1))
                
    for a in range(0,len(bottom)):                                                      # display bounce labels
        bottom_surface=font.render(["","+"][bottom[a][0]>0]+str(bottom[a][0]),1,white)
        screen.blit(bottom_surface, (bottom[a][1], height-scale))
    for a in range(0,len(top)):
        top_surface=font.render(["","+"][top[a][0]>0]+str(top[a][0]),1,white)
        screen.blit(top_surface, (top[a][1], scale//2))
    for a in range(0,len(left)):
        left_surface=font.render(["","+"][left[a][0]>0]+str(left[a][0]),1,white)
        screen.blit(left_surface, (scale//2, left[a][1]))
    for a in range(0,len(right)):
        right_surface=font.render(["","+"][right[a][0]>0]+str(right[a][0]),1,white)
        screen.blit(right_surface, (width-scale, right[a][1]))
        
    pygame.draw.rect(screen, blue, (width-scale,0, scale, scale))                       # draw 4 buttons and the ball
    pygame.draw.rect(screen, orange, (0,height-scale, scale, scale))
    pygame.draw.rect(screen, red, (0,0, scale, scale))
    pygame.draw.rect(screen, green, (width-scale,height-scale, scale, scale))
    pygame.draw.circle(screen, orange, ball, max(scale//4,1))
    
    time_text="t= "+str((t//scale)-1)                                                   # display time
    time_surface=font.render(time_text, 1, white)
    
    screen.blit(time_surface, (width//2,0))                                             # update
    pygame.display.flip()
    clock.tick(s)
    
pygame.display.quit()
