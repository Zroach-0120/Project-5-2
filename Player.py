from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, Filename, CollisionSphere
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Drone, Missile
import math, random

class Spaceship(SphereCollideObject):
    def __init__(self, loader: Loader, taskMgr, accept: Callable[[str, Callable], None], 
                 modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, 
                 posVec: Vec3, scaleVec: float, camera):

        
        super().__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 0.01)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName)
        
        self.loader = loader
        self.render = parentNode
        self.accept = accept
    
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.taskMgr = taskMgr
        self.camera = camera
        self.zoom_factor = 5
        self.cameraZoomSpeed = 10
        self.modelNode.setHpr(0, -90, 0)
      
        #self.collisionNode.node().addSolid(CollisionSphere(0, 0, 0, 1.0))
        self.collisionNode.show()


        #self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)


        self.reloadTime = 0.25
        self.missileDistance = 4000
        self.missileBay = 1
        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)
        
        

    def CheckIntervals(self, task):
        for i in list(Missile.Intervals.keys()):
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()
                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + ' has reached the end of its fire solution')
        return Task.cont

    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            
            tag = 'Missile' + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront
            currentMissile = Missile(self.loader, "./Assets/Phaser/phaser.egg", self.render, tag, posVec, 4.0)
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos=posVec, fluid=1)
            Missile.Intervals[tag].start()
        else:
           if not self.taskMgr.hasTaskNamed('reload'):
                print('Initializing reload...')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont  
#
    def Reload(self, task):
        if task.time > self.reloadtime: 
           self.missileBay += 1
        if self.missileBay > 1:
            self.missileBay = 1
            print("Reload complete")
            return Task.done
        elif task.time <= self.reloadTime:
            print("reload proceeding")
            return Task.cont




    def move_forward(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyMoveForward, 'move-forward')
        else:
            self.taskMgr.remove('move-forward')

    def ApplyMoveForward(self, task):
        rate = 5
        direction = self.modelNode.getQuat().getForward()
        self.modelNode.setPos(self.modelNode.getPos() + direction * rate)
        return Task.cont

    def turn_left(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnLeft, 'turn-left')
        else:
            self.taskMgr.remove('turn-left')

    def ApplyTurnLeft(self, task):
        self.modelNode.setH(self.modelNode.getH() + 1.5)
        return Task.cont

    def turn_right(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnRight, 'turn-right')
        else:
            self.taskMgr.remove('turn-right')

    def ApplyTurnRight(self, task):
        self.modelNode.setH(self.modelNode.getH() - 1.5)
        return Task.cont

    def turn_up(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnUp, 'turn-up')
        else:
            self.taskMgr.remove('turn-up')

    def ApplyTurnUp(self, task):
        self.modelNode.setP(self.modelNode.getP() - 1.5)
        return Task.cont

    def turn_down(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyTurnDown, 'turn-down')
        else:
            self.taskMgr.remove('turn-down')

    def ApplyTurnDown(self, task):
        self.modelNode.setP(self.modelNode.getP() + 1.5)
        return Task.cont

    def roll_left(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRollLeft, 'roll-left')
        else:
            self.taskMgr.remove('roll-left')

    def ApplyRollLeft(self, task):
        self.modelNode.setR(self.modelNode.getR() + 2.0)
        return Task.cont

    def roll_right(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRollRight, 'roll-right')
        else:
            self.taskMgr.remove('roll-right')

    def ApplyRollRight(self, task):
        self.modelNode.setR(self.modelNode.getR() - 2.0)
        return Task.cont

    def UpdateCamera(self, task):
        target_pos = self.modelNode.getPos() + Vec3(0, -30, 10)
        current_pos = self.camera.getPos()
        new_pos = current_pos + (target_pos - current_pos) * 0.1
        self.camera.setPos(new_pos)
        self.camera.lookAt(self.modelNode)
        return Task.cont

    def set_camera(self):
        self.UpdateCamera(None)

    def zoom_in(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyZoomIn, 'zoom-in')
        else:
            self.taskMgr.remove('zoom-in')

    def ApplyZoomIn(self, task):
        self.camera.setPos(self.camera.getPos() + Vec3(0, self.cameraZoomSpeed, 0))
        return Task.cont

    def zoom_out(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyZoomOut, 'zoom-out')
        else:
            self.taskMgr.remove('zoom-out')

    def ApplyZoomOut(self, task):
        self.camera.setPos(self.camera.getPos() + Vec3(0, -self.cameraZoomSpeed, 0))
        return Task.cont

    def attach_drone_rings(self, numDronesPerRing=12, radius=20):
        ringParent = self.modelNode.attachNewNode("AllDroneRings")
        angleStep = 2 * math.pi / numDronesPerRing

        for axis in ['x', 'y', 'z']:
            for i in range(numDronesPerRing):
                angle = i * angleStep
                pos = Vec3()
                if axis == 'x':
                    pos.y = math.cos(angle) * radius
                    pos.z = math.sin(angle) * radius
                elif axis == 'y':
                    pos.x = math.cos(angle) * radius
                    pos.z = math.sin(angle) * radius
                elif axis == 'z':
                    pos.x = math.cos(angle) * radius
                    pos.y = math.sin(angle) * radius
                Drone(
                    self.loader,
                    "./Assets/DroneDefender/DroneDefender.obj",
                    ringParent,
                    f"Drone-{axis}-{i}",
                    "./Assets/DroneDefender/octotoad1_auv.png",
                    pos,
                    .5
                )