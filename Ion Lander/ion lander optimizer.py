#Part Parameters
#Constant Dry Mass = 40kg (Probe Core) + 5kg (Ladder) + 50kg (Reaction Wheel) + 5kg (Panel for recharging on the surface) = 100kg
#EC is 0.05kg per unit, in 100 unit batches
#Xenon is 0.1kg/unit
#Xenon tanks
#Radial has 405 Xenon, dry mass 14kg
#Tiny has 720 Xenon, dry mass 24kg
#Small has 5700 Xenon, dry mass 190kg
#Ion engine weighs 250kg Thrust 2,000N EC 8.741/s Xenon 0.486/s

import math as math
import copy

class Craft:
    charge = 0
    chargeCapacity = 0
    xenon = 0
    radialTanks = 0
    tinyTanks = 0
    smallTanks = 0
    ionEngines = 0

    def __init__(self, chargeCapacity, radialTanks, tinyTanks, smallTanks, xenon, ionEngines = 1):
        self.chargeCapacity = chargeCapacity
        self.charge = chargeCapacity
        self.radialTanks = radialTanks
        self.tinyTanks = tinyTanks
        self.smallTanks = smallTanks
        self.xenon = xenon
        self.ionEngines = ionEngines

    def GetMass(self):
        return 100 + self.ionEngines * 250 + self.chargeCapacity * 0.05 + self.xenon * 0.1 + self.radialTanks * 14 + self.tinyTanks * 24 + self.smallTanks * 190
    def GetAcc(self):
        return self.ionEngines * 2_000 / self.GetMass()

class Planet:
    gravitationalParameter = 0
    landingRadius = 0
    rotationVelocity = 0
    def __init__(self, grav, radius, rotationVelocity):
        self.gravitationalParameter = grav
        self.landingRadius = radius
        self.rotationVelocity = rotationVelocity


def ConstantAltitudeLanding(planet, craft, logging=True):
    craft.charge = craft.chargeCapacity
    velocity = math.sqrt(planet.gravitationalParameter / planet.landingRadius)
    escapeCode = 0
    while True:
        #Physics frame (1 second)
        thrust = craft.GetAcc()
        gravity = planet.gravitationalParameter / planet.landingRadius**2 - velocity**2 / planet.landingRadius
        if gravity > thrust:
            escapeCode = "Not Enough TWR"
            break
        effectiveThrust = math.sqrt(thrust**2 - gravity**2)
        velocity -= effectiveThrust
        if velocity < planet.rotationVelocity:
            escapeCode = "Successful Landing"
            break
        #Alter the craft
        craft.charge -= craft.ionEngines * 8.741
        craft.xenon -= craft.ionEngines * 0.486
        #Staging of Xenon tanks
        smallestTank = 5700
        if craft.tinyTanks > 0:
            smallestTank = 720
        if craft.radialTanks > 0:
            smallestTank = 405
        if craft.radialTanks*405 + craft.tinyTanks*720 + craft.smallTanks*5700 - craft.xenon > smallestTank:
            if smallestTank == 405:
                craft.radialTanks -= 1
                print("Staged Radial Tank")
            if smallestTank == 720:
                craft.tinyTanks -= 1
                print("Staged Tiny Tank")
        #Out of fuel escape codes
        if craft.charge < 0:
            escapeCode = "Flat Battery"
            break
        if craft.xenon < 0:
            escapeCode = "Ran Out Of Fuel"
            break
        if logging:
            print("Speed: "+str(velocity)+" Acceleration: "+str(thrust)+" Gravity: "+str(gravity)+" Xenon: "+str(craft.xenon)+" EC: "+str(craft.charge))
    if logging:
        print(escapeCode)
    return [craft, escapeCode]

def ConstantAltitudeLaunch(planet, craft, logging=True):
    velocity = planet.rotationVelocity
    escapeCode = 0
    craft.charge = craft.chargeCapacity
    while True:
        #Physics frame (1 second)
        thrust = craft.GetAcc()
        gravity = planet.gravitationalParameter / planet.landingRadius**2 - velocity**2 / planet.landingRadius
        if gravity > thrust:
            escapeCode = "Not Enough TWR"
            break
        effectiveThrust = math.sqrt(thrust**2 - gravity**2)
        velocity += effectiveThrust
        if gravity < 0:
            escapeCode = "Successful Launch"
            break
        #Alter the craft
        craft.charge -= craft.ionEngines * 8.741
        craft.xenon -= craft.ionEngines * 0.486
        #Staging of Xenon tanks
        smallestTank = 5700
        if craft.tinyTanks > 0:
            smallestTank = 720
        if craft.radialTanks > 0:
            smallestTank = 405
        if craft.radialTanks*405 + craft.tinyTanks*720 + craft.smallTanks*5700 - craft.xenon > smallestTank:
            if smallestTank == 405:
                craft.radialTanks -= 1
                print("Staged Radial Tank")
            if smallestTank == 720:
                craft.tinyTanks -= 1
                print("Staged Tiny Tank")
        #Out of fuel escape codes
        if craft.charge < 0:
            escapeCode = "Flat Battery"
            break
        if craft.xenon < 0:
            escapeCode = "Ran Out Of Fuel"
            break
        if logging:
            print("Speed: "+str(velocity)+" Acceleration: "+str(thrust)+" Gravity: "+str(gravity)+" Xenon: "+str(craft.xenon)+" EC: "+str(craft.charge))
    if logging:
        print(escapeCode)
    return escapeCode

def CombinedTest(craft, planet):
    landingResult = ConstantAltitudeLanding(planet, craft, False)
    if landingResult[1] != "Successful Landing":
        return landingResult[1]
    launchResult = ConstantAltitudeLaunch(planet, landingResult[0], False)
    return launchResult

def Optimize(planet):
    craft = Craft(100,1,0,0,10,1)
    testingResult = ""
    while testingResult != "Successful Launch" and craft.chargeCapacity < 10000:
        testingResult = CombinedTest(copy.deepcopy(craft), planet)
        match testingResult:
            case "Flat Battery":
                craft.chargeCapacity += 100
            case "Ran Out Of Fuel":
                craft.xenon += 10
                #Re-allocate Xenon tanks to best hold more fuel
                if craft.xenon > craft.radialTanks*405 + craft.tinyTanks*720 + craft.smallTanks*5700:
                    if craft.radialTanks > 0:
                        craft.radialTanks -= 1
                        craft.tinyTanks += 1
                    else:
                        craft.radialTanks += 2
                        craft.tinyTanks -= 1
            case "Not Enough TWR":
                craft.ionEngines += 1
    return craft 


mercury = Planet(2.2*10**13, 2440000, 0)
moon = Planet(4.903*10**12, 1737000, 4.5)
phobos = Planet(7.088*10**5, 7000, 0)
deimos = Planet(9.616*10**4, 5000, 0)
vesta = Planet(1.729*10**10, 263000, 86)
ceres = Planet(6.263*10**10, 473000, 92)
io = Planet(5.96*10**12, 1811000, 75)
europa = Planet(3.203*10**12, 1551000, 32)
ganymede = Planet(9_888_471_600_000, 2_624_000, 26.8)
callisto = Planet(7.179*10**12, 2409000, 11)
mimas = Planet(2.504*10**9, 198000, 15)
enceladus = Planet(7.211*10**9, 252000, 14)
tethys = Planet(4.121*10**10, 531000, 20)
dione = Planet(7.312*10*10, 561000, 15)
rhea = Planet(1.539*10*11, 764000, 12)
iapetus = Planet(1.205*10**11, 735000, 0)
miranda = Planet(4.32*10**9, 236000, 12)
ariel = Planet(8.346*10**10, 579000, 17)
umbriel = Planet(8.509*10**10, 585000, 0)
titania = Planet(2.269*10**11, 789000, 0)
oberon = Planet(2.053*10**11, 761000, 0)
triton = Planet(1.428*10**12, 1353000, 17)
pluto = Planet(8.696*10**11, 1187000, 14)
charon = Planet(1.059*10**11, 604000, 7)

SolarSystem = [mercury, moon, phobos, deimos, vesta, ceres, io, europa, ganymede, callisto, mimas,
               enceladus, tethys, dione, rhea, iapetus, miranda, ariel, umbriel, titania, oberon, triton, pluto, charon]
results = []
for planet in SolarSystem:
    result = Optimize(planet)
    if result.chargeCapacity > 9999:
        results.append("Not Possible with just batteries")
    else:
        results.append("EC: "+str(result.chargeCapacity)+" Xenon: "+str(result.xenon)+" Radial Tanks: "+str(result.radialTanks)+" Tiny Tanks: "+str(result.tinyTanks)+" Engines: "+str(result.ionEngines))
    print(planet)
for result in results:
    print(result)
