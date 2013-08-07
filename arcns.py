# -*- coding: utf-8 -*-

from panda3d.core import loadPrcFile

loadPrcFile("misc/config.prc")

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Parallel
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.filter.CommonFilters import CommonFilters
from direct.stdpy.file import *
from panda3d.core import Point3, Vec4, Vec3, BitMask32, NodePath, PandaNode, TextNode
from panda3d.core import PointLight, DirectionalLight, Spotlight, AmbientLight, PerspectiveLens
from panda3d.core import LightRampAttrib, WindowProperties, Filename
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay
from panda3d.core import Geom, GeomNode, GeomVertexData, GeomVertexFormat, GeomVertexWriter, GeomPrimitive, GeomTriangles

import direct.directbase.DirectStart
import math, sys, json

#fonction for arrow square
def square_arrow():
    vdata = GeomVertexData("square",GeomVertexFormat.getV3c4(),Geom.UHStatic)
    vertex = GeomVertexWriter(vdata,"vertex"); color = GeomVertexWriter(vdata,"color")
    vertex.addData3f(1,-0.8,-0.1); vertex.addData3f(1,0.6,-0.1); vertex.addData3f(-1,0.6,-0.1); vertex.addData3f(-1,-0.8,-0.1)
    color.addData4f(1,0,0,1); color.addData4f(1,0,0,1); color.addData4f(1,0,0,1); color.addData4f(1,0,0,1)
    prim = GeomTriangles(Geom.UHStatic); prim.addVertices(0,1,2); prim.addVertices(0,2,3)
    geom = Geom(vdata); geom.addPrimitive(prim); node = GeomNode("square_arrow"); node.addGeom(geom)
    nodp = render.attachNewNode(node); nodp.hide(); nodp.node().setIntoCollideMask(BitMask32.bit(1))
    return nodp

#main scene class
class mainScene:
    def __init__(self,app):
        self.app = app
        camera.setPos(0,-62,12); camera.setHpr(0,-10,0)
        #lights
        dlghtnode = DirectionalLight("dir light"); dlghtnode.setColor(Vec4(0.8,0.8,0.8,1))
        dlght_top = render.attachNewNode(dlghtnode); dlght_top.setHpr(0,-70,0); render.setLight(dlght_top)
        self.app.lst_lghts.append(dlght_top)
        dlght_right = render.attachNewNode(dlghtnode); dlght_right.setHpr(-30,-10,0); render.setLight(dlght_right)
        self.app.lst_lghts.append(dlght_right)
        dlght_left = render.attachNewNode(dlghtnode); dlght_left.setHpr(30,-10,0); render.setLight(dlght_left)
        self.app.lst_lghts.append(dlght_left)
        spotnode = Spotlight("spot_aux_menu"); spotnode.setColor(Vec4(0.8,0.8,0.8,1)); lens = PerspectiveLens(); spotnode.setLens(lens)
        spotlght = render.attachNewNode(spotnode); render.setLight(spotlght)
        spotlght.lookAt(6,-0.5,-1.5); spotlght.setPos(-8,0,9); self.app.lst_lghts.append(spotlght)
        #decors
        self.lst_decor = []
        arcs_shower = loader.loadModel("models/static/main_arcs_show"); arcs_shower.reparentTo(render)
        arcs_shower.setPos(0,7.3,3); self.lst_decor.append(arcs_shower)
        arcs_shower_hprInterv = arcs_shower.hprInterval(5,Point3(360,0,0),startHpr=Point3(0,0,0))
        arcs_shower_pace = Sequence(arcs_shower_hprInterv,name="arcs_shower_pace"); arcs_shower_pace.loop()
        arc_title = loader.loadModel("models/static/main_title"); arc_title.reparentTo(render)
        self.lst_decor.append(arc_title)
        #arc_main_menu
        self.arc_main_menu = Actor("models/dynamic/main_m_menu"); self.arc_main_menu.reparentTo(render); self.arc_main_menu.pose("load",1)
        #arc_aux_menu
        #
        #TODO
        #
        self.arc_aux_menu = Actor("models/dynamic/main_a_menu"); self.arc_aux_menu.reparentTo(render)
        #
        #self.arc_aux_menu.loop("basic")
        #
        #
        #arrows (FOR MAIN MENU)
        arr_up = render.attachNewNode("arrow-up"); arr_up.setHpr(0,90,0); arr_up.setPos(4.5,1.5,7); arr_up.hide()
        self.app.arrow.instanceTo(arr_up); arr_up.reparentTo(self.app.pickly_node)
        self.app.lst_arrows.append({"name":"arr_up","status":0,"node":arr_up,"posn":[4.5,1.5,7],"posh":[4.5,1.7,7.2]})
        sqp_up = square_arrow(); sqp_up.node().setTag("arrow","up"); sqp_up.reparentTo(self.app.pickly_node)
        sqp_up.setPos(4.5,1.5,7); sqp_up.setHpr(180,-90,0)
        arr_dn = render.attachNewNode("arrow-dn"); arr_dn.setHpr(180,-90,0); arr_dn.setPos(4.5,1.5,5); arr_dn.hide()
        self.app.arrow.instanceTo(arr_dn); arr_dn.reparentTo(self.app.pickly_node)
        self.app.lst_arrows.append({"name":"arr_dn","status":0,"node":arr_dn,"posn":[4.5,1.5,5],"posh":[4.5,1.7,4.8]})
        sqp_dn = square_arrow(); sqp_dn.node().setTag("arrow","dn"); sqp_dn.reparentTo(self.app.pickly_node)
        sqp_dn.setPos(4.5,1.5,5); sqp_dn.setHpr(0,90,0)
        #
        #
        #TODO : add other arrows
        #
        #
        #gates
        self.gates = Actor("models/dynamic/main_gates"); self.gates.reparentTo(render)
        self.gates.setPos(0,-48.2,9.5); self.gates.setHpr(0,80,0); self.gates.play("open_gates")
        #env
        self.sol = base.loader.loadModel("models/static/main_sol"); self.sol.reparentTo(render); self.sol.setPos(0,0,0)
        self.roofs = base.loader.loadModel("models/static/main_roofs"); self.roofs.reparentTo(render); self.roofs.setPos(0,0,0)
        #GUI
        self.lst_menus = [0,0,0] #0 -> which menu, 1 -> val main_menu, 2 -> val aux_menu
        self.lst_gui = []
        #GUI : frames
        main_frame = DirectFrame(); main_frame.hide(); self.lst_gui.append(main_frame)
        camp_frame = DirectFrame(); camp_frame.hide(); self.lst_gui.append(camp_frame)
        mission_frame = DirectFrame(); mission_frame.hide(); self.lst_gui.append(mission_frame)
        option_frame = DirectFrame(); option_frame.hide(); self.lst_gui.append(option_frame)
        #GUI : main menu
        campaign_btn = DirectButton(text=self.app.lang["main_menu"]["campaign"],scale=0.12,pos=(-0.15,0,-0.2),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft,command=self.valid_main_menu)
        campaign_btn._DirectGuiBase__componentInfo["text2"][0].setFg((0.04,0.3,0.8,1))
        campaign_btn.reparentTo(main_frame); campaign_btn["state"] = DGG.DISABLED; self.lst_gui.append(campaign_btn)
        mission_btn = DirectButton(text=self.app.lang["main_menu"]["mission"],scale=0.1,pos=(-0.19,0,-0.34),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft,command=self.valid_main_menu)
        mission_btn._DirectGuiBase__componentInfo["text2"][0].setFg((0.04,0.3,0.8,1))
        mission_btn.reparentTo(main_frame); mission_btn["state"] = DGG.DISABLED; self.lst_gui.append(mission_btn)
        options_btn = DirectButton(text=self.app.lang["main_menu"]["options"],scale=0.09,pos=(-0.26,0,-0.47),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft,command=self.valid_main_menu)
        options_btn._DirectGuiBase__componentInfo["text2"][0].setFg((0.04,0.3,0.8,1))
        options_btn.reparentTo(main_frame); options_btn["state"] = DGG.DISABLED; self.lst_gui.append(options_btn)
        quit_btn = DirectButton(text=self.app.lang["main_menu"]["quit"],scale=0.07,pos=(-0.35,0,-0.58),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft,command=self.valid_main_menu)
        quit_btn._DirectGuiBase__componentInfo["text2"][0].setFg((0.04,0.3,0.8,1))
        quit_btn.reparentTo(main_frame); quit_btn["state"] = DGG.DISABLED; self.lst_gui.append(quit_btn)
        #GUI : aux_menu -> campaign
        #
        #TODO
        #
        #
        #
        camp_stitre = DirectLabel(text=self.app.lang["camp_menu"]["stitre"],scale=0.12,pos=(-1,0,0.7),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft)
        #
        camp_stitre.reparentTo(camp_frame)
        #
        #camp_start = DirectButton(text=self)
        #
        #text2 : over
        #text3 : disabled
        #
        #camp_start.reparentTo(camp_frame)
        #
        camp_cancel = DirectButton(text=self.app.lang["camp_menu"]["return_btn"],scale=0.09,pos=(-0.9,0,0.55),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft,command=self.aux_quitmenu)
        camp_cancel._DirectGuiBase__componentInfo["text2"][0].setFg((0.04,0.3,0.8,1))
        camp_cancel.reparentTo(camp_frame); self.lst_gui.append(camp_cancel)
        #
        #GUI : aux_menu -> missions
        #
        #TODO
        #
        mission_stitre = DirectLabel(text=self.app.lang["mission_menu"]["stitre"],scale=0.12,pos=(-1,0,0.7),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft)
        #
        mission_stitre.reparentTo(mission_frame)
        #
        #
        #
        #GUI : aux_menu -> options
        #
        #TODO
        #
        option_stitre = DirectLabel(text=self.app.lang["option_menu"]["stitre"],scale=0.12,pos=(-1,0,0.7),text_bg=(1,1,1,0.8),
            relief=None,text_font=self.app.arcFont,text_align=TextNode.ALeft)
        #
        option_stitre.reparentTo(option_frame)
        #
        #
        #
        #delayed tasks
        taskMgr.doMethodLater(6.5,self.main_start_task,"main start task")
        taskMgr.doMethodLater(9,self.main_stmm_task,"main start main menu task")
        taskMgr.doMethodLater(11,self.main_affmm_task,"main aff main menu task")
        #
        #models (TODO)
        #
        #
    def main_start_task(self,task):
        cam_move = camera.posInterval(4,Point3(0,-25,12)); cam_move.start()
        return task.done
    def main_stmm_task(self,task):
        self.arc_main_menu.play("load")
        return task.done
    def main_affmm_task(self,task):
        self.lst_gui[0].show(); self.lst_gui[self.lst_menus[1]+4]["state"] = DGG.NORMAL
        self.app.lst_arrows[0]["node"].show(); self.app.lst_arrows[0]["status"] = 1; self.app.lst_arrows[1]["status"] = 1
        #capture de la souris
        self.app.wp.setCursorHidden(False); base.win.requestProperties(self.app.wp)
        self.app.accept("mouse1",self.main_m_menu_state_change,[2])
        self.app.accept("wheel_up",self.main_m_menu_state_change,[0])
        self.app.accept("wheel_down",self.main_m_menu_state_change,[1])
        #capture du clavier
        self.app.accept("arrow_up",self.main_m_menu_state_change,[0])
        self.app.accept("arrow_down",self.main_m_menu_state_change,[1])
        self.app.accept("enter",self.valid_main_menu)
        #capture du over arrow geom
        self.mouseTask = taskMgr.add(self.main_mouse_task,"main_mouse_task")
        return task.done
    def main_mouse_task(self,task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.app.pickerRay.setFromLens(base.camNode,mpos.getX(),mpos.getY())
            self.app.mouse_trav.traverse(self.app.pickly_node)
            if self.app.mouse_hand.getNumEntries() > 0:
                if self.lst_menus[0] == 0:
                    tag = self.app.mouse_hand.getEntry(0).getIntoNode().getTag("arrow")
                    if tag == "up": nod = self.app.lst_arrows[0]
                    elif tag == "dn": nod = self.app.lst_arrows[1]
                    nod["status"] = 2; nod["node"].setPos(nod["posh"][0],nod["posh"][1],nod["posh"][2])
                elif self.lst_menus[0] == 1:
                    #
                    #TODO : WAITING FOR THE AUX MENU SHOW BEFORE
                    #
                    #
                    #
                    pass
            else:
                for e in self.app.lst_arrows:
                    if e["status"] == 2:
                        e["node"].setPos(e["posn"][0],e["posn"][1],e["posn"][2])
                        e["status"] = 1
        return task.cont
    def main_m_menu_state_change(self,sens):
        if sens == 2: #capture depuis le click souris
            if self.app.lst_arrows[0]["status"] == 2: sens = 0
            elif self.app.lst_arrows[1]["status"] == 2: sens = 1
            else: return
        pos_texts = [(-0.35,0,0.23),(-0.26,0,0.1),(-0.19,0,-0.04),(-0.15,0,-0.2),(-0.19,0,-0.34),(-0.26,0,-0.47),(-0.35,0,-0.58)]
        scale_texts = [0.07,0.09,0.1,0.12,0.1,0.09,0.07]
        self.lst_gui[self.lst_menus[1]+4]["state"] = DGG.DISABLED
        if sens == 0 and self.lst_menus[1] < 3:
            if self.lst_menus[1] == 0: self.app.lst_arrows[1]["node"].show()
            if self.lst_menus[1] == 2: self.app.lst_arrows[0]["node"].hide()
            self.arc_main_menu.play("state_"+str(self.lst_menus[1])+"_"+str(self.lst_menus[1]+1)); self.lst_menus[1] += 1
        elif sens == 1 and self.lst_menus[1] > 0:
            if self.lst_menus[1] == 1: self.app.lst_arrows[1]["node"].hide()
            if self.lst_menus[1] == 3: self.app.lst_arrows[0]["node"].show()
            self.arc_main_menu.play("state_"+str(self.lst_menus[1])+"_"+str(self.lst_menus[1]-1)); self.lst_menus[1] -= 1
        movePara = Parallel(name="texts_move")
        for it in range(4,8):
            movePara.append(self.lst_gui[it].posInterval(0.5,Point3(pos_texts[3-self.lst_menus[1]+it-4])))
            movePara.append(self.lst_gui[it].scaleInterval(0.5,scale_texts[3-self.lst_menus[1]+it-4]))
        movePara.start(); self.lst_gui[self.lst_menus[1]+4]["state"] = DGG.NORMAL
    def valid_main_menu(self):
        self.app.wp.setCursorHidden(True); base.win.requestProperties(self.app.wp)
        self.app.ignore("mouse1"); self.app.ignore("wheel_up"); self.app.ignore("wheel_down")
        self.app.ignore("arrow_up"); self.app.ignore("arrow_down"); self.app.ignore("enter")
        if self.lst_menus[1] == 0 or self.lst_menus[1] == 1:
            #
            #TODO : liste des sauvegardes disponibles
            #
            pass
        if self.lst_menus[1] == 0:
            #
            #TODO : remove all possible old infos
            #
            pass
        elif self.lst_menus[1] == 1:
            #
            #TODO : reset ?
            #
            #
            pass
        elif self.lst_menus[1] == 2:
            #
            #TODO : reset all last config unvalid
            #
            pass
        elif self.lst_menus[1] == 3: sys.exit(0)
        self.app.lst_arrows[0]["node"].hide(); self.app.lst_arrows[1]["node"].hide(); self.lst_gui[0].hide()
        movePara = Parallel(name="main_to_aux")
        movePara.append(camera.posInterval(2,Point3(-4,-1,7)))
        movePara.append(camera.hprInterval(2,Point3(-90,-10,0)))
        movePara.start()
        taskMgr.doMethodLater(2.5,self.aux_affmenu_task,"main aff aux menu task")
        self.lst_menus[0] = 1
    def aux_affmenu_task(self,task):
        self.app.wp.setCursorHidden(False); base.win.requestProperties(self.app.wp)
        self.lst_gui[self.lst_menus[1]+1].show()
        #
        #TODO : re accept all the inputs
        #
        self.app.accept("escape",self.aux_quitmenu)
        self.app.accept("backspace",self.aux_quitmenu)
        #
        #
        return task.done
    def aux_quitmenu(self):
        self.lst_gui[self.lst_menus[1]+1].hide()
        self.app.accept("escape",sys.exit,[0]); self.app.ignore("backspace")
        #
        #TODO : ignore inputs
        #
        movePara = Parallel(name="aux_to_main")
        movePara.append(camera.posInterval(2,Point3(0,-25,12)))
        movePara.append(camera.hprInterval(2,Point3(0,-10,0)))
        movePara.start()
        taskMgr.doMethodLater(2.5,self.main_affmm_task,"main aff main menu task")
    def valid_aux_menu(self):
        #
        #
        #
        pass
    def change_lang(self):
        #
        #
        #
        #
        pass
    def close_main_scene(self):
        #
        #TODO
        #
        #self.arc_main_menu
        #self.arc_aux_menu
        #
        #self.app.ignore("mouse1")
        #self.app.ignore("wheel_up")
        #self.app.ignore("wheel_down")
        #self.app.ignore("arrow_up")
        #self.app.ignore("arrow_down")
        #self.app.ignore("enter")
        #taskMgr.main_mouse_task()
        #clear pickly_node children
        #
        pass

#game scene class
class game_scene:
    def __init__(self):
        #
        #TODO
        #
        pass

#class ArcnsApp(DirectObject):
class ArcnsApp(DirectObject):
    def __init__(self): #basic init start
        base.disableMouse()
        self.wp = WindowProperties(); self.wp.setCursorFilename(Filename.binaryFilename("misc/cursors/main_cursor.ico"))
        self.wp.setCursorHidden(True); base.win.requestProperties(self.wp)
        self.arcFont = base.loader.loadFont("misc/firstv2.ttf")
        textVersion = OnscreenText(text="v0.0",font=self.arcFont,pos=(1.15,-0.95),fg=(0,0,0,1),bg=(1,1,1,0.8))
        base.setBackgroundColor(1,1,1)
        self.main_config = json.loads("".join([line.rstrip() for line in file("misc/config.json","rb")]))
        #arrows (GENERAL)
        self.arrow = loader.loadModel("models/static/arrow"); self.lst_arrows = []
        #light ramp
        self.rampnode = NodePath(PandaNode("temp node"))
        self.rampnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.1,0.7))
        self.rampnode.setShaderAuto()
        base.cam.node().setInitialState(self.rampnode.getState())
        #ink filter
        self.filters = CommonFilters(base.win,base.cam)
        self.filterok = self.filters.setCartoonInk(separation=1)
        #keyboard inputs
        self.accept("escape",sys.exit,[0])
        #
        #TEMP TEST
        self.accept("q",sys.exit,[0])
        #TEMP TEST
        #
        #
        #lights
        self.lst_lghts = []
        #ambient light (permanent)
        self.alghtnode = AmbientLight("amb light"); self.alghtnode.setColor(Vec4(0.4,0.4,0.4,1))
        self.alght = render.attachNewNode(self.alghtnode); render.setLight(self.alght)
        #language recup
        self.langtab = self.main_config["lang"][self.main_config["lang_chx"]]
        self.lang = json.loads("".join([line.rstrip() for line in file("misc/lang/"+self.langtab[0]+".json","rb")]))
        #mouse handler
        self.mouse_trav = CollisionTraverser(); self.mouse_hand = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay'); self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay(); self.pickerNode.addSolid(self.pickerRay)
        self.mouse_trav.addCollider(self.pickerNP,self.mouse_hand)
        self.pickly_node = render.attachNewNode("pickly_node")
        #init main scene
        self.scene = mainScene(self)
    def change_screen(self):
        #
        #TODO and TEST
        #
        wp = WindowProperties()
        #
        wp.setSize(200,200)
        #
        base.win.requestProperties(wp)
        #

app = ArcnsApp()
run()
