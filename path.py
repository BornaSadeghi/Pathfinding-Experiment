from pygame import *
import gui, math, geometry
init()
SIZE = 600,600
screen = display.set_mode(SIZE)

gridW, gridH = 20,20
cellSpacing = 0

cellSize = SIZE[0]/gridW - cellSpacing

WHITE = 255,255,255
LIGHTGREY = 245,245,245

wallColour = 100,100,100
pathColour = 150,200,255
visColour = 200,255,150 # visited cells
startColour = 0,255,0
endColour = 255,0,0

maxDist = 1000
showDist = False
diagonals = True
heuristic = True
terminateWhenPathFound = False

class Cell:
    def __init__(self, x=0, y=0, originalColour=WHITE):
        self.x, self.y = x,y
        self.rect = x*cellSize + x*cellSpacing, y*cellSize + y*cellSpacing, cellSize, cellSize
        self.wall = False
        self.dist = maxDist
        self.visited = False
        
        self.originalColour = originalColour

        self.distText = gui.SimpleText(self.rect, str(self.dist), 10)
        self.path = False # is part of the path?
    def draw(self):
        if self == startCell:
            colour = startColour
        elif self == endCell:
            colour = endColour
        elif self.path:
            colour = pathColour
#         elif self.visited:
#             colour = visColour
        else:
            colour = wallColour if self.wall else self.originalColour
        draw.rect(screen, colour, self.rect)
        
        if showDist and self.dist < maxDist:
            self.distText.update(str(self.dist))
            self.distText.draw()

def getHoveredCell ():
    
    return grid[int(mouseX//cellSize)][int(mouseY//cellSize)]

def resetNodes ():
    for col in grid:
        for cell in col:
#             cell.visited = False
            cell.path = False
            cell.dist = maxDist

def clearWalls():
    for col in grid:
        for cell in col:
            cell.wall = False
    calcPath()

def drawPath (x,y):
    dist = grid[x][y].dist
    
    for i in range (dist):
        if x < gridW-1 and grid[x+1][y].dist == grid[x][y].dist-1: # right
            x += 1
        elif grid[x-1][y].dist == grid[x][y].dist-1: # left
            x -= 1
        elif y < gridH-1 and grid[x][y+1].dist == grid[x][y].dist-1: # down
            y += 1
        elif grid[x][y-1].dist == grid[x][y].dist-1: # up
            y -= 1
            
        elif diagonals:
            if x > 0 and y > 0 and grid[x-1][y-1].dist == grid[x][y].dist-1: # up left
                x -= 1
                y -= 1
            elif x > 0 and y < gridH-1 and grid[x-1][y+1].dist == grid[x][y].dist-1: # down left
                x -= 1
                y += 1
            elif x < gridW-1 and y > 0 and grid[x+1][y-1].dist == grid[x][y].dist-1: # up right
                x += 1
                y -= 1
            elif x < gridW-1 and y < gridH-1 and grid[x+1][y+1].dist == grid[x][y].dist-1: # down right
                x += 1
                y += 1
        else:
            break
            
        grid[x][y].path = True


def getNextNodes (x,y):
    nextNodes = []
    if 0 < x and not grid[x-1][y].wall:
        nextNodes.append((x-1, y))
        
    if x < gridW-1 and not grid[x+1][y].wall:
        nextNodes.append((x+1, y))
        
    if 0 < y and not grid[x][y-1].wall:
        nextNodes.append((x, y-1))
        
    if y < gridH-1 and not grid[x][y+1].wall:
        nextNodes.append((x, y+1))
        
    if diagonals:
        if 0 < x and 0 < y and not grid[x-1][y-1].wall:
            nextNodes.append((x-1, y-1))
            
        if 0 < x and y < gridH-1 and not grid[x-1][y+1].wall:
            nextNodes.append((x-1, y+1))
                
        if x < gridW-1 and 0 < y and not grid[x+1][y-1].wall:
            nextNodes.append((x+1, y-1))
            
        if x < gridW-1 and y < gridH-1 and not grid[x+1][y+1].wall:
            nextNodes.append((x+1, y+1))
    return nextNodes

def dfs (x,y):
    global calls
    if terminateWhenPathFound:
        if endCell.dist < maxDist:
            return
    
    calls += 1
    grid[x][y].visited = True
    nextNodes = getNextNodes(x, y)
    if heuristic:
        nextNodes.sort(key=byDist)
            
    for nx,ny in nextNodes:
        if grid[nx][ny].dist > grid[x][y].dist + 1:
            grid[nx][ny].dist = grid[x][y].dist + 1
            dfs(nx, ny)
            
                
def drawCells ():
    for col in grid:
        for cell in col:
            cell.draw()

def calcPath ():
    global calls
    calls = 0
    resetNodes()
    if startCell != None and endCell != None:
        startCell.dist = 0
        dfs(startCell.x, startCell.y)
        drawPath(endCell.x, endCell.y)
        print("Recursive calls: %d" %calls)

# function for sorting cells by distance to end
def byDist (cellPos):
    return geometry.distance(cellPos, (endCell.x, endCell.y))

grid = []
for col in range (gridW):
    grid.append([])
    for row in range (gridH):
        grid[col].append(Cell(col,row, WHITE if (row+col)%2==0 else LIGHTGREY))

calls = 0

startCell = None
endCell = None

mouseHold1 = False
mouseHold3 = False
hovered = None
run = True
while run:
    mouseX, mouseY = mouse.get_pos()
    
    drawCells()
    
    if mouseHold1: # LMB
        if hovered != None:
            hovered.wall = True
            if hovered.path:
                calcPath()
    elif mouseHold3: # RMB
        if hovered != None and hovered.wall:
            hovered.wall = False
            calcPath()
    
    for e in event.get():
        if e.type == MOUSEMOTION:
            hovered = getHoveredCell()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 1: # LMB
                mouseHold1 = True
            elif e.button == 3: # RMB
                mouseHold3 = True
            elif e.button == 4: # wheel up
                if hovered != None:
                    startCell = hovered
                    calcPath()
            elif e.button == 5: # wheel down
                if hovered != None:
                    endCell = hovered
                    calcPath()
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: # LMB
                mouseHold1 = False
            elif e.button == 3: # RMB
                mouseHold3 = False
        elif e.type == KEYDOWN:
            if e.key == K_1:
                print("Walls cleared")
                clearWalls()
            elif e.key == K_2:
                terminateWhenPathFound = not terminateWhenPathFound
                print("Terminate when path found" if terminateWhenPathFound else "Continue when path found")
                calcPath()
            elif e.key == K_3:
                showDist = not showDist
                print("Distances shown" if showDist else "Distances hidden")
            elif e.key == K_4:
                heuristic = not heuristic
                print("Heuristic on" if heuristic else "Heuristic off")
            elif e.key == K_5:
                diagonals = not diagonals
                print("Diagonals" if diagonals else "No diagonals")
                calcPath()
        elif e.type == QUIT:
            run = False
            
    display.update()
quit()