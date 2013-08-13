# -*- coding: utf-8 -*-

from panda3d.core import loadPrcFile

loadPrcFile("config.prc")

from direct.showbase.DirectObject import DirectObject
from direct.showbase.AppRunnerGlobal import appRunner
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Parallel
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from direct.filter.CommonFilters import CommonFilters
from direct.stdpy.file import *
from panda3d.core import Point3, Vec4, Vec3, BitMask32, NodePath, PandaNode, TextNode
from panda3d.core import PointLight, DirectionalLight, Spotlight, AmbientLight, PerspectiveLens
from panda3d.core import LightRampAttrib, WindowProperties, Filename, CardMaker
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay
from panda3d.core import Geom, GeomNode, GeomVertexData, GeomVertexFormat, GeomVertexWriter, GeomPrimitive, GeomTriangles
from pandac.PandaModules import TransparencyAttrib

import direct.directbase.DirectStart
import math, os, sys, json

#from direct.tkpanels.inspector import inspect

"""
override functions
"""
def arcButton(txt,pos,cmd,scale=0.08,txtalgn=TextNode.ALeft,extraArgs=[]): #override button
    ndp = DirectButton(text=txt,scale=scale,text_font=arcFont,pos=pos,text_bg=(1,1,1,0.8),relief=None,text_align=txtalgn,
        command=cmd,extraArgs=extraArgs)
    ndp._DirectGuiBase__componentInfo["text2"][0].setFg((0.03,0.3,0.8,1))
    ndp._DirectGuiBase__componentInfo["text3"][0].setFg((0.3,0.3,0.3,1))
    return ndp

def arcLabel(txt,pos,scale=0.08,txtalgn=TextNode.ALeft): #override label
    ndp = DirectLabel(text=txt,scale=scale,pos=pos,text_bg=(1,1,1,0.8),relief=None,text_font=arcFont,text_align=txtalgn)
    return ndp

def arcOptMenu(txt,pos,items,init=0,cmd=None,scale=0.08,change=1,txtalgn=TextNode.ALeft,extraArgs=[]):
    ndp = DirectOptionMenu(text=txt,scale=scale,pos=pos,items=items,initialitem=init,textMayChange=change,text_font=arcFont,
        text_align=txtalgn,text_bg=(1,1,1,0.8),relief=None,highlightColor=(0.03,0.3,0.8,1),popupMarker_relief=None,
        popupMarker_pos=(0,0,0),popupMarkerBorder=(0,0),item_text_font=arcFont,command=cmd,extraArgs=extraArgs)
    return ndp

def arcRadioButton(lst_rad,parent,gui,scale=0.08,txtalgn=TextNode.ALeft): #override radio button
    lst_radio = []
    for elt in lst_rad:
        ndp = DirectRadioButton(text=elt[0],variable=elt[1],value=elt[2],command=elt[3],extraArgs=elt[4],
            text_align=txtalgn,scale=scale,pos=elt[5],text_font=arcFont,text_bg=(1,1,1,0.8),relief=None)
        lst_radio.append(ndp)
    for elt in lst_radio:
        elt.setOthers(lst_radio); elt.reparentTo(parent); gui.append(elt)

def arcEntry(pos,txt="",cmd=None,scale=0.08,nlines=1): #override entry
    ndp = DirectEntry(pos=pos,text=txt,command=cmd,scale=scale,numLines=nlines,entryFont=arcFont,frameColor=(1,1,1,0.8),relief=DGG.RIDGE)
    return ndp

"""
scenes classes
"""
class mainScene: #main scene class
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
        self.arc_aux_menu = Actor("models/dynamic/main_a_menu"); self.arc_aux_menu.reparentTo(render); self.arc_aux_menu.pose("load",1)
        #arrows for main menu
        arr_up = render.attachNewNode("arrow-up"); arr_up.setHpr(0,90,0); arr_up.setPos(4.5,1.5,7); arr_up.hide()
        self.app.arrow.instanceTo(arr_up); arr_up.reparentTo(render)
        self.app.lst_arrows.append({"name":"arr_up","status":0,"node":arr_up,"posn":[4.5,1.5,7],"posh":[4.5,1.7,7.2]})
        sqp_up = render.attachNewNode(self.app.c_arr.generate()); sqp_up.hide(); sqp_up.node().setIntoCollideMask(BitMask32.bit(1))
        sqp_up.node().setTag("arrow","up"); sqp_up.reparentTo(self.app.pickly_node); sqp_up.setPos(4.5,1.5,7)
        arr_dn = render.attachNewNode("arrow-dn"); arr_dn.setHpr(180,-90,0); arr_dn.setPos(4.5,1.5,5); arr_dn.hide()
        self.app.arrow.instanceTo(arr_dn); arr_dn.reparentTo(render)
        self.app.lst_arrows.append({"name":"arr_dn","status":0,"node":arr_dn,"posn":[4.5,1.5,5],"posh":[4.5,1.7,4.8]})
        sqp_dn = render.attachNewNode(self.app.c_arr.generate()); sqp_dn.hide(); sqp_dn.node().setIntoCollideMask(BitMask32.bit(1))
        sqp_dn.node().setTag("arrow","dn"); sqp_dn.reparentTo(self.app.pickly_node); sqp_dn.setPos(4.5,1.5,5.2)
        #arrows for campaign menu
        #
        arr_camp_up = render.attachNewNode("arr-camp-up"); arr_camp_up.setScale(0.5); arr_camp_up.setHpr(-90,90,0); arr_camp_up.setPos(8,-2.5,7)
        arr_camp_up.hide(); self.app.arrow.instanceTo(arr_camp_up); arr_camp_up.reparentTo(render)
        self.app.lst_arrows.append({"name":"arr_camp_up","status":0,"node":arr_camp_up,"posn":[8,-2.5,7],"posh":[8.1,-2.5,7.1]})
        #
        sqp_c_up = render.attachNewNode(self.app.c_arr.generate()); sqp_c_up.hide(); sqp_c_up.node().setIntoCollideMask(BitMask32.bit(1))
        sqp_c_up.node().setTag("arrow_c","up"); sqp_c_up.reparentTo(self.app.pickly_node)
        sqp_c_up.setScale(0.5); sqp_c_up.setHpr(-90,0,0); sqp_c_up.setPos(8,-2.5,7)
        #
        #
        arr_camp_dn = render.attachNewNode("arr-camp-dn"); arr_camp_dn.setScale(0.5); arr_camp_dn.setHpr(90,-90,0); arr_camp_dn.setPos(8,-2.5,2)
        arr_camp_dn.hide(); self.app.arrow.instanceTo(arr_camp_dn); arr_camp_up.reparentTo(render)
        self.app.lst_arrows.append({"name":"arr_camp_dn","status":0,"node":arr_camp_dn,"posn":[8,-2.5,2],"posh":[8.1,-2.5,1.9]})
        #
        sqp_c_dn = render.attachNewNode(self.app.c_arr.generate()); sqp_c_dn.hide(); sqp_c_dn.node().setIntoCollideMask(BitMask32.bit(1))
        sqp_c_dn.node().setTag("arrow_c","dn"); sqp_c_dn.reparentTo(self.app.pickly_node)
        sqp_c_dn.setScale(0.5); sqp_c_dn.setHpr(-90,0,0); sqp_c_dn.setPos(8,-2.5,2.1)
        #
        #
        #arrows for missions menu
        #
        #TODO : arrows up/down for mission selection
        #
        #TODO : arrows up/down for save selection
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
        self.lst_gui = {"frames":[],"main_frame":[],"camp_frame":[],"mission_frame":[],"option_frame":[],"saves":[]}
        #GUI : frames
        main_frame = DirectFrame(); main_frame.hide(); self.lst_gui["frames"].append(main_frame)
        camp_frame = DirectFrame(); camp_frame.hide(); self.lst_gui["frames"].append(camp_frame)
        mission_frame = DirectFrame(); mission_frame.hide(); self.lst_gui["frames"].append(mission_frame)
        option_frame = DirectFrame(); option_frame.hide(); self.lst_gui["frames"].append(option_frame)
        #GUI : main menu
        campaign_btn = arcButton(self.app.lang["main_menu"]["campaign"],(-0.15,0,-0.2),self.valid_main_menu,scale=0.12)
        campaign_btn.reparentTo(main_frame); campaign_btn["state"] = DGG.DISABLED; self.lst_gui["main_frame"].append(campaign_btn)
        mission_btn = arcButton(self.app.lang["main_menu"]["mission"],(-0.19,0,-0.34),self.valid_main_menu,scale=0.1)
        mission_btn.reparentTo(main_frame); mission_btn["state"] = DGG.DISABLED; self.lst_gui["main_frame"].append(mission_btn)
        options_btn = arcButton(self.app.lang["main_menu"]["options"],(-0.26,0,-0.47),self.valid_main_menu,scale=0.09)
        options_btn.reparentTo(main_frame); options_btn["state"] = DGG.DISABLED; self.lst_gui["main_frame"].append(options_btn)
        quit_btn = arcButton(self.app.lang["main_menu"]["quit"],(-0.35,0,-0.58),self.valid_main_menu,scale=0.07)
        quit_btn.reparentTo(main_frame); quit_btn["state"] = DGG.DISABLED; self.lst_gui["main_frame"].append(quit_btn)
        #GUI : aux_menu -> campaign
        camp_stitre = arcLabel(self.app.lang["camp_menu"]["stitre"],(-1,0,0.7),0.13)
        camp_stitre.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_stitre)
        camp_create_lab = arcLabel(self.app.lang["camp_menu"]["new_unit"],(-1.1,0,0.4))
        camp_create_lab.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_create_lab)
        camp_entry = arcEntry((-1,0,0.25),cmd=self.crea_unit); camp_entry.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_entry)
        camp_create = arcButton(self.app.lang["camp_menu"]["crea_unit"],(-0.3,0,0.4),self.crea_unit)
        camp_create.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_create)
        camp_used = arcLabel(self.app.lang["camp_menu"]["used_name"],(-1,0,0.1))
        camp_used.reparentTo(camp_frame); camp_used.hide(); self.lst_gui["camp_frame"].append(camp_used)
        camp_select_lab = arcLabel(self.app.lang["camp_menu"]["sel_lab"],(0.1,0,0.4))
        camp_select_lab.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_select_lab)
        camp_play = arcButton(self.app.lang["camp_menu"]["launch"],(0,0,-0.2),self.valid_aux_menu)
        camp_play.hide(); camp_play.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_play)
        camp_remove = arcButton(self.app.lang["camp_menu"]["supp_unit"],(0.3,0,-0.2),self.supp_unit)
        camp_remove.hide(); camp_remove.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_remove)
        camp_nosave = arcLabel(self.app.lang["camp_menu"]["no_unit"],(0,0,0))
        camp_nosave.hide(); camp_nosave.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_nosave)
        camp_cancel = arcButton(self.app.lang["aux_menu"]["return_btn"],(-1,0,-0.7),self.aux_quitmenu)
        camp_cancel.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_cancel)
        camp_time = arcLabel("",(1.25,0,0),0.07,TextNode.ARight); camp_time.hide()
        camp_time.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_time)
        camp_date = arcLabel("",(1.25,0,-0.08),0.07,TextNode.ARight); camp_date.hide()
        camp_date.reparentTo(camp_frame); self.lst_gui["camp_frame"].append(camp_date)
        #GUI : aux_menu -> missions
        mission_stitre = arcLabel(self.app.lang["mission_menu"]["stitre"],(-1,0,0.7),0.13)
        mission_stitre.reparentTo(mission_frame); self.lst_gui["mission_frame"].append(mission_stitre)
        #
        #
        #TODO : all the mission form is missing
        #
        #
        mission_cancel = arcButton(self.app.lang["aux_menu"]["return_btn"],(-1,0,-0.7),self.aux_quitmenu)
        mission_cancel.reparentTo(mission_frame); self.lst_gui["mission_frame"].append(mission_cancel)
        #GUI : aux_menu -> options
        option_stitre = arcLabel(self.app.lang["option_menu"]["stitre"],(-1,0,0.7),0.13)
        option_stitre.reparentTo(option_frame); self.lst_gui["option_frame"].append(option_stitre)
        self.opt_var = {"chg":[False,False,False],"fullscreen":[self.app.main_config["fullscreen"]],
            "size_chx":self.app.main_config["size_chx"],"lang_chx":self.app.main_config["lang_chx"]}
        lst_rad = [[self.app.lang["option_menu"]["windowed"],self.opt_var["fullscreen"],[False],self.opt_change,[0],(-1.1,0,0.4)],
            [self.app.lang["option_menu"]["fullscreen"],self.opt_var["fullscreen"],[True],self.opt_change,[0],(-1.1,0,0.3)]]
        arcRadioButton(lst_rad,option_frame,self.lst_gui["option_frame"])
        self.lst_gui["option_frame"][1]["indicatorValue"] = (0 if self.opt_var["fullscreen"][0] else 1)
        self.lst_gui["option_frame"][2]["indicatorValue"] = (1 if self.opt_var["fullscreen"][0] else 0)
        opt_chx_res_lab = arcLabel(self.app.lang["option_menu"]["res_chx"],(-1.1,0,0))
        opt_chx_res_lab.reparentTo(option_frame); self.lst_gui["option_frame"].append(opt_chx_res_lab)
        opt_chx_res = arcOptMenu(self.app.main_config["size"][self.app.main_config["size_chx"]],(-0.4,0,0),self.app.main_config["size"],
            init=self.app.main_config["size_chx"],cmd=self.opt_change,extraArgs=[1])
        opt_chx_res.reparentTo(option_frame); self.lst_gui["option_frame"].append(opt_chx_res)
        opt_chx_lang_lab = arcLabel(self.app.lang["option_menu"]["lang_chx"],(-1.1,0,-0.2))
        opt_chx_lang_lab.reparentTo(option_frame); self.lst_gui["option_frame"].append(opt_chx_lang_lab)
        lst_lang = []
        for elt in self.app.main_config["lang"]: lst_lang.append(elt[1])
        opt_chx_lang = arcOptMenu(self.app.main_config["lang"][self.app.main_config["lang_chx"]][1],(-0.4,0,-0.2),lst_lang,
            init=self.app.main_config["lang_chx"],cmd=self.opt_change,extraArgs=[2])
        opt_chx_lang.reparentTo(option_frame); self.lst_gui["option_frame"].append(opt_chx_lang)
        opt_valid = arcButton(self.app.lang["option_menu"]["btn_valid"],(0,0,-0.7),self.opt_action,extraArgs=[0]); opt_valid["state"] = DGG.DISABLED
        opt_valid.reparentTo(option_frame); self.lst_gui["option_frame"].append(opt_valid)
        opt_reset = arcButton(self.app.lang["option_menu"]["btn_reset"],(0.4,0,-0.7),self.opt_action,extraArgs=[1]); opt_reset["state"] = DGG.DISABLED
        opt_reset.reparentTo(option_frame); self.lst_gui["option_frame"].append(opt_reset)
        option_cancel = arcButton(self.app.lang["aux_menu"]["return_btn"],(-1,0,-0.7),self.aux_quitmenu)
        option_cancel.reparentTo(option_frame); self.lst_gui["option_frame"].append(option_cancel)
        #delayed tasks
        taskMgr.doMethodLater(6.5,self.main_start_task,"main start task")
        taskMgr.doMethodLater(9,self.main_stmm_task,"main start main menu task")
        taskMgr.doMethodLater(11,self.main_affmm_task,"main aff main menu task")
        #
        #TODO : models
        #
        #
    def main_start_task(self,task):
        cam_move = camera.posInterval(4,Point3(0,-25,12)); cam_move.start()
        return task.done
    def main_stmm_task(self,task):
        self.arc_main_menu.play("load")
        return task.done
    def main_affmm_task(self,task):
        self.app.change_cursor(1); self.nomove = True; self.lst_gui["frames"][0].show()
        self.lst_gui["main_frame"][self.lst_menus[1]]["state"] = DGG.NORMAL
        if self.lst_menus[1] > 0: self.app.lst_arrows[1]["node"].show()
        if self.lst_menus[1] < 3: self.app.lst_arrows[0]["node"].show()
        self.app.lst_arrows[0]["status"] = 1; self.app.lst_arrows[1]["status"] = 1
        #capture de la souris
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
            if self.app.mouse_hand.getNumEntries() > 0 and self.nomove:
                if self.lst_menus[0] == 0:
                    tag = self.app.mouse_hand.getEntry(0).getIntoNode().getTag("arrow")
                    if tag == "up": nod = self.app.lst_arrows[0]
                    elif tag == "dn": nod = self.app.lst_arrows[1]
                    nod["status"] = 2; nod["node"].setPos(nod["posh"][0],nod["posh"][1],nod["posh"][2])
                elif self.lst_menus[0] == 1:
                    if self.lst_menus[1] == 0:
                        tag = self.app.mouse_hand.getEntry(0).getIntoNode().getTag("arrow_c")
                        if tag == "up": nod = self.app.lst_arrows[2]
                        elif tag == "dn": nod = self.app.lst_arrows[3]
                        nod["status"] = 2; nod["node"].setPos(nod["posh"][0],nod["posh"][1],nod["posh"][2])
                    elif self.lst_menus[1] == 1:
                        #
                        #TODO : action des arrows pour le sous menu "missions"
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
        self.lst_gui["main_frame"][self.lst_menus[1]]["state"] = DGG.DISABLED
        if sens == 0 and self.lst_menus[1] < 3:
            if self.lst_menus[1] == 0: self.app.lst_arrows[1]["node"].show()
            if self.lst_menus[1] == 2: self.app.lst_arrows[0]["node"].hide()
            self.arc_main_menu.play("state_"+str(self.lst_menus[1])+"_"+str(self.lst_menus[1]+1)); self.lst_menus[1] += 1
        elif sens == 1 and self.lst_menus[1] > 0:
            if self.lst_menus[1] == 1: self.app.lst_arrows[1]["node"].hide()
            if self.lst_menus[1] == 3: self.app.lst_arrows[0]["node"].show()
            self.arc_main_menu.play("state_"+str(self.lst_menus[1])+"_"+str(self.lst_menus[1]-1)); self.lst_menus[1] -= 1
        movePara = Parallel(name="texts_move")
        for it in range(4):
            movePara.append(self.lst_gui["main_frame"][it].posInterval(0.5,Point3(pos_texts[3-self.lst_menus[1]+it])))
            movePara.append(self.lst_gui["main_frame"][it].scaleInterval(0.5,scale_texts[3-self.lst_menus[1]+it]))
        movePara.start(); self.lst_gui["main_frame"][self.lst_menus[1]]["state"] = DGG.NORMAL
    def valid_main_menu(self):
        self.nomove = False; self.app.change_cursor(0); taskMgr.doMethodLater(1,self.main_aux_arcs_task,"anim aux arcs task")
        self.app.ignore("escape"); self.app.ignore("mouse1"); self.app.ignore("wheel_up"); self.app.ignore("wheel_down")
        self.app.ignore("arrow_up"); self.app.ignore("arrow_down"); self.app.ignore("enter")
        self.app.lst_arrows[0]["status"] = 0; self.app.lst_arrows[1]["status"] = 0
        self.app.lst_arrows[0]["node"].hide(); self.app.lst_arrows[1]["node"].hide()
        self.nb_saves = 0; self.lst_saves = []; self.gui_saves = []
        if self.lst_menus[1] == 0 or self.lst_menus[1] == 1:
            if exists(self.app.curdir+"/saves"):
                self.lst_saves = os.listdir(self.app.curdir+"/saves"); self.nb_saves = len(self.lst_saves)
                if self.nb_saves > 0:
                    for it,elt in enumerate(self.lst_saves):
                        date_save = elt[:-5].split("_"); date_save[1] = date_save[1].replace("-",":"); date_save = " ".join(date_save)
                        cur_save = json.loads("".join([line.rstrip().lstrip() for line in file(self.app.curdir+"/saves/"+elt,"rb")]))
                        time_txt = ""
                        if cur_save["time"] < 100: time_txt = str(cur_save["time"])+" s"
                        elif cur_save["time"] < 6000:
                            s = cur_save["time"] % 60; m = (cur_save["time"]-s) / 60; time_txt = str(m)+":"+str(s)
                        else:
                            s = cur_save["time"] % 60; tm = (cur_save["time"]-s) / 60; m = tm%60; h = (tm-m)/60
                            time_txt = str(h)+":"+str(m)+":"+str(s)
                        self.gui_saves.append([cur_save["nom"],date_save,time_txt,it,None])
            else: os.makedirs(self.app.curdir+"/saves")
        if self.lst_menus[1] == 0:
            if len(self.lst_gui["camp_frame"]) > 12:
                for it in range(12,len(self.lst_gui["camp_frame"])):
                    self.lst_gui["camp_frame"][12].removeNode(); del self.lst_gui["camp_frame"][12]
            for elt in self.gui_saves:
                save_lab = arcLabel(elt[0],(0,0,0)); save_lab.reparentTo(self.lst_gui["frames"][1]); save_lab.hide()
                self.lst_gui["camp_frame"].append(save_lab); elt[4] = save_lab
        elif self.lst_menus[1] == 1:
            #
            #TODO : action à faire lors de l'activation du sous menu "missions"
            #
            #
            pass
        elif self.lst_menus[1] == 3: sys.exit(0)
        self.app.lst_arrows[0]["node"].hide(); self.app.lst_arrows[1]["node"].hide(); self.lst_gui["frames"][0].hide()
        movePara = Parallel(name="main_to_aux")
        movePara.append(camera.posInterval(2,Point3(-4,-1,7)))
        movePara.append(camera.hprInterval(2,Point3(-90,-10,0)))
        movePara.start()
        taskMgr.doMethodLater(2.5,self.aux_affmenu_task,"main aff aux menu task")
        self.lst_menus[0] = 1
    def main_aux_arcs_task(self,task):
        self.arc_aux_menu.play("load")
        return task.done
    def aux_affmenu_task(self,task):
        self.app.change_cursor(1); self.nomove = True; self.lst_gui["frames"][self.lst_menus[1]+1].show()
        self.app.accept("escape",self.aux_quitmenu); self.app.accept("backspace",self.aux_quitmenu)
        if self.lst_menus[1] == 0:
            self.app.lst_arrows[2]["status"] = 1; self.app.lst_arrows[3]["status"] = 1
            #capture du clavier
            self.app.accept("arrow_up",self.move_camp_unit,[0]); self.app.accept("arrow_down",self.move_camp_unit,[1])
            self.app.accept("enter",self.valid_aux_menu)
            #capture de la souris
            self.app.accept("mouse1",self.move_camp_unit,[2]); self.app.accept("wheel_up",self.move_camp_unit,[0])
            self.app.accept("wheel_down",self.move_camp_unit,[1])
            if self.nb_saves == 0: self.lst_gui["camp_frame"][8].show()
            else:
                self.lst_gui["camp_frame"][6].show(); self.lst_gui["camp_frame"][7].show()
                self.lst_gui["camp_frame"][10]["text"] = self.gui_saves[0][2]; self.lst_gui["camp_frame"][10].show() #time
                self.lst_gui["camp_frame"][11]["text"] = self.gui_saves[0][1]; self.lst_gui["camp_frame"][11].show() #date
                self.gui_saves[0][4].show(); self.gui_saves[0][4].setScale(0.1)
                if self.nb_saves > 1:
                    self.gui_saves[1][4].show(); self.gui_saves[1][4].setScale(0.08); self.gui_saves[1][4].setPos(0.3,0,-0.5)
                    if self.nb_saves > 2:
                        self.gui_saves[2][4].show(); self.gui_saves[2][4].setScale(0.07); self.gui_saves[2][4].setPos(0.4,0,-0.6)
                        if self.nb_saves > 3:
                            self.gui_saves[3][4].show(); self.gui_saves[3][4].setScale(0.05); self.gui_saves[3][4].setPos(0.5,0,-0.68)
                if self.nb_saves > 1: self.app.lst_arrows[2]["node"].show()
        elif self.lst_menus[1] == 1:
            #
            #TODO : création des labels et remplissage des tableaux pour le sous menu "missions"
            #
            pass
        elif self.lst_menus[1] == 2: self.app.accept("enter",self.opt_action,[0])
        return task.done
    def aux_quitmenu(self):
        self.nomove = False; self.app.change_cursor(0); self.lst_gui["frames"][self.lst_menus[1]+1].hide(); self.arc_aux_menu.play("unload")
        self.app.accept("escape",sys.exit,[0]); self.app.ignore("backspace"); self.app.ignore("enter")
        self.app.ignore("arrow_up"); self.app.ignore("arrow_down")
        if self.lst_menus[1] == 0: #campaign
            self.app.lst_arrows[2]["status"] = 0; self.app.lst_arrows[3]["status"] = 0
            self.app.lst_arrows[2]["node"].hide(); self.app.lst_arrows[3]["node"].hide()
        elif self.lst_menus[1] == 1: #missions
            #
            #TODO : arrows pour le sous menu "missions"
            #
            #
            pass
        #
        movePara = Parallel(name="aux_to_main"); movePara.append(camera.posInterval(2,Point3(0,-25,12)))
        movePara.append(camera.hprInterval(2,Point3(0,-10,0))); movePara.start()
        taskMgr.doMethodLater(2.5,self.main_affmm_task,"main aff main menu task"); self.lst_menus[0] = 0
    def valid_aux_menu(self):
        #
        #TODO : validation pour lancement d'une partie (campagne ou mission)
        #
        pass
    def crea_unit(self):
        #
        #TODO : création d'une unité, avec le fichier correspondant, et l'ajout du label
        #
        pass
    def supp_unit(self):
        #
        #TODO : suppression d'une unité, avec le fichier et les labels correspondants
        #
        pass
    def move_camp_unit(self,sens):
        if sens == 2: #capture depuis le click souris
            if self.app.lst_arrows[2] == 2: sens = 0
            elif self.app.lst_arrows[3] == 2: sens = 1
            else: return
        #
        """
        self.lst_gui["main_frame"][self.lst_menus[1]]["state"] = DGG.DISABLED
        if sens == 0 and self.lst_menus[1] < 3:
            if self.lst_menus[1] == 0: self.app.lst_arrows[1]["node"].show()
            if self.lst_menus[1] == 2: self.app.lst_arrows[0]["node"].hide()
            self.arc_main_menu.play("state_"+str(self.lst_menus[1])+"_"+str(self.lst_menus[1]+1)); self.lst_menus[1] += 1
        elif sens == 1 and self.lst_menus[1] > 0:
            if self.lst_menus[1] == 1: self.app.lst_arrows[1]["node"].hide()
            if self.lst_menus[1] == 3: self.app.lst_arrows[0]["node"].show()
            self.arc_main_menu.play("state_"+str(self.lst_menus[1])+"_"+str(self.lst_menus[1]-1)); self.lst_menus[1] -= 1
        movePara = Parallel(name="texts_move")
        for it in range(4):
            movePara.append(self.lst_gui["main_frame"][it].posInterval(0.5,Point3(pos_texts[3-self.lst_menus[1]+it])))
            movePara.append(self.lst_gui["main_frame"][it].scaleInterval(0.5,scale_texts[3-self.lst_menus[1]+it]))
        movePara.start(); self.lst_gui["main_frame"][self.lst_menus[1]]["state"] = DGG.NORMAL
        """
        #
        pos_texts = [(0.3,0,0.2),(0,0,0),(0.3,0,-0.5),(0.4,0,-0.6),(0.5,0,-0.68)]
        scale_texts = [0.08,0.1,0.08,0.08,0.05]
        #
        print "move_camp_unit"
        print sens
        #
        #TODO : déplacement des labels
        #
        #
    def opt_change(self,val,chx=0):
        if chx == 0 and val == 0: self.opt_var["chg"][0] = (False if self.opt_var["fullscreen"][0] == self.app.main_config["fullscreen"] else True)
        elif chx == 1:
            idx = self.app.main_config["size"].index(val)
            self.opt_var["chg"][1] = (False if self.app.main_config["size_chx"] == idx else True)
            self.opt_var["size_chx"] = idx
        elif chx == 2:
            idx = [i for i,x in enumerate(self.app.main_config["lang"]) if x[1] == val][0]
            self.opt_var["chg"][2] = (False if self.app.main_config["lang_chx"] == idx else True)
            self.opt_var["lang_chx"] = idx
        disab = DGG.DISABLED
        for elt in self.opt_var["chg"]:
            if elt == True:
                disab = DGG.NORMAL
                break
        if len(self.lst_gui["option_frame"]) == 10:
            self.lst_gui["option_frame"][-3]["state"] = disab
            self.lst_gui["option_frame"][-2]["state"] = disab
    def opt_action(self,act):
        self.lst_gui["option_frame"][-3]["state"] = DGG.DISABLED
        self.lst_gui["option_frame"][-2]["state"] = DGG.DISABLED
        if self.opt_var["chg"][0]:
            if act == 0: self.app.main_config["fullscreen"] = self.opt_var["fullscreen"][0]
            elif act == 1:
                self.opt_var["fullscreen"][0] = self.app.main_config["fullscreen"]
                self.lst_gui["option_frame"][1]["indicatorValue"] = (0 if self.opt_var["fullscreen"][0] else 1)
                self.lst_gui["option_frame"][2]["indicatorValue"] = (1 if self.opt_var["fullscreen"][0] else 0)
        if self.opt_var["chg"][1]:
            if act == 0: self.app.main_config["size_chx"] = self.opt_var["size_chx"]
            elif act == 1:
                self.opt_var["size_chx"] = self.app.main_config["size_chx"]
                self.lst_gui["option_frame"][4].set(self.opt_var["size_chx"])
        if self.opt_var["chg"][2]:
            if act == 0:
                self.app.main_config["lang_chx"] = self.opt_var["lang_chx"]
                self.app.langtab = self.app.main_config["lang"][self.app.main_config["lang_chx"]]
                self.app.lang = json.loads("".join([line.rstrip().lstrip() for line in file("misc/lang/"+self.app.langtab[0]+".json","rb")]))
                self.lst_gui["main_frame"][0]["text"] = self.app.lang["main_menu"]["campaign"]
                self.lst_gui["main_frame"][1]["text"] = self.app.lang["main_menu"]["mission"]
                self.lst_gui["main_frame"][2]["text"] = self.app.lang["main_menu"]["options"]
                self.lst_gui["main_frame"][3]["text"] = self.app.lang["main_menu"]["quit"]
                self.lst_gui["camp_frame"][0]["text"] = self.app.lang["camp_menu"]["stitre"]
                self.lst_gui["camp_frame"][1]["text"] = self.app.lang["camp_menu"]["new_unit"]
                self.lst_gui["camp_frame"][3]["text"] = self.app.lang["camp_menu"]["crea_unit"]
                self.lst_gui["camp_frame"][4]["text"] = self.app.lang["camp_menu"]["used_name"]
                self.lst_gui["camp_frame"][5]["text"] = self.app.lang["camp_menu"]["sel_lab"]
                self.lst_gui["camp_frame"][6]["text"] = self.app.lang["camp_menu"]["launch"]
                self.lst_gui["camp_frame"][7]["text"] = self.app.lang["camp_menu"]["supp_unit"]
                self.lst_gui["camp_frame"][8]["text"] = self.app.lang["camp_menu"]["no_unit"]
                self.lst_gui["camp_frame"][9]["text"] = self.app.lang["aux_menu"]["return_btn"]
                #
                #TODO : ajout de la traduction pour le sous menu "missions"
                #
                #
                self.lst_gui["mission_frame"][0]["text"] = self.app.lang["mission_menu"]["stitre"]
                #self.lst_gui["mission_frame"][0]["text"] = #
                #
                self.lst_gui["option_frame"][0]["text"] = self.app.lang["option_menu"]["stitre"]
                self.lst_gui["option_frame"][1]["text"] = self.app.lang["option_menu"]["windowed"]
                self.lst_gui["option_frame"][2]["text"] = self.app.lang["option_menu"]["fullscreen"]
                self.lst_gui["option_frame"][3]["text"] = self.app.lang["option_menu"]["res_chx"]
                self.lst_gui["option_frame"][5]["text"] = self.app.lang["option_menu"]["lang_chx"]
                self.lst_gui["option_frame"][7]["text"] = self.app.lang["option_menu"]["btn_valid"]
                self.lst_gui["option_frame"][8]["text"] = self.app.lang["option_menu"]["btn_reset"]
                self.lst_gui["option_frame"][9]["text"] = self.app.lang["aux_menu"]["return_btn"]
            elif act == 1:
                self.opt_var["lang_chx"] = self.app.main_config["lang_chx"]
                self.lst_gui["option_frame"][6].set(self.opt_var["lang_chx"])
        if act == 0 and not self.opt_var["chg"] == [False,False,False]:
            conf = open(self.app.curdir+"/config.json","w"); conf.write(json.dumps(self.app.main_config)); conf.close()
        if not self.opt_var["chg"] == [False,False,False]: self.opt_var["chg"] = [False,False,False]
    def close_main_scene(self):
        #
        #TODO : fermeture de la scène principale, avec destruction de la plupart des éléments
        #
        #self.arc_main_menu
        #self.arc_aux_menu
        #
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

class cine_scene: #cinematic scene class
    def __init__(self):
        #
        #TODO : initialisation d'une scène de cinématique
        #
        pass

class game_scene: #game scene class
    def __init__(self):
        #
        #TODO : initialisation d'une scène de jeu
        #
        pass


class ArcnsApp(DirectObject): #class ArcnsApp, main class
    def __init__(self): #basic init start
        base.disableMouse(); self.wp = WindowProperties(); self.wp.setCursorHidden(True); base.win.requestProperties(self.wp)
        cm = CardMaker("cursor"); cm.setFrame(0,0.1,-0.13,0); self.cust_mouse = render.attachNewNode(cm.generate())
        self.cust_mouse_tex = []
        self.cust_mouse_tex.append(loader.loadTexture("models/cursors/blank_cursor.png"))
        self.cust_mouse_tex.append(loader.loadTexture("models/cursors/main_cursor.png"))
        self.cust_mouse.setTexture(self.cust_mouse_tex[0])
        self.cust_mouse.setTransparency(TransparencyAttrib.MAlpha)
        self.cust_mouse.reparentTo(render2d); self.cust_mouse.setBin("gui-popup",100)
        base.mouseWatcherNode.setGeometry(self.cust_mouse.node())
        #text and background
        textVersion = OnscreenText(text="v0.0",font=arcFont,pos=(1.15,-0.95),fg=(0,0,0,1),bg=(1,1,1,0.8))
        base.setBackgroundColor(1,1,1)
        self.curdir = (appRunner.p3dFilename.getDirname() if appRunner else "..")
        self.main_config = json.loads("".join([line.rstrip().lstrip() for line in file(self.curdir+"/config.json","rb")]))
        #arrows (GENERAL)
        self.arrow = loader.loadModel("models/static/arrow"); self.lst_arrows = []
        self.c_arr = CardMaker("arrow_hide"); self.c_arr.setFrame(-1,1,-0.8,0.6)
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
        #lights
        self.lst_lghts = []
        #ambient light (permanent)
        self.alghtnode = AmbientLight("amb light"); self.alghtnode.setColor(Vec4(0.4,0.4,0.4,1))
        self.alght = render.attachNewNode(self.alghtnode); render.setLight(self.alght)
        #language recup
        self.langtab = self.main_config["lang"][self.main_config["lang_chx"]]
        self.lang = json.loads("".join([line.rstrip().lstrip() for line in file("misc/lang/"+self.langtab[0]+".json","rb")]))
        #mouse handler
        self.mouse_trav = CollisionTraverser(); self.mouse_hand = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay'); self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay(); self.pickerNode.addSolid(self.pickerRay)
        self.mouse_trav.addCollider(self.pickerNP,self.mouse_hand)
        self.pickly_node = render.attachNewNode("pickly_node")
        #init main scene
        self.scene = mainScene(self)
    def change_cursor(self,chx):
        self.cust_mouse.setTexture(self.cust_mouse_tex[chx])
    def change_screen(self):
        #
        #TODO : changement de la résolution
        #TODO : ouverture d'une nouvelle fenêtre (uniquement accessible avec l'option "windowed" activée)
        #
        wp = WindowProperties()
        #
        wp.setSize(200,200)
        #
        base.win.requestProperties(wp)
        #

arcFont = base.loader.loadFont("misc/firstv2.ttf")
app = ArcnsApp()
run()
