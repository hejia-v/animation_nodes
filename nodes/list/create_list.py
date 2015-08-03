import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... utils.mn_node_utils import getNotUsedSocketName
from ... utils.selection import getSortedSelectedObjectNames
from ... sockets.mn_socket_info import (getListBaseSocketIdNames,
                                       getSocketClassFromIdName,
                                       getIdNameFromDataType,
                                       getListSocketIdName)

def getListTypeItems(self, context):
    items = []
    for baseIdName in getListBaseSocketIdNames():
        socketClass = getSocketClassFromIdName(baseIdName)
        dataType = socketClass.dataType
        items.append((dataType, dataType, ""))
    return items

class CreateList(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CreateList"
    bl_label = "Create List"

    def settingChanged(self, context):
        for socket in self.inputs:
            socket.moveable = self.manageSockets
            socket.removeable = self.manageSockets
            socket.hide = self.hideInputs

    def assignedTypeChanged(self, context):
        baseDataType = self.assignedType
        self.baseIdName = getIdNameFromDataType(baseDataType)
        self.listIdName = getListSocketIdName(self.baseIdName)
        self.recreateSockets()

    selectedType = EnumProperty(name = "Type", items = getListTypeItems)
    assignedType = StringProperty(update = assignedTypeChanged)
    baseIdName = StringProperty()
    listIdName = StringProperty()

    manageSockets = BoolProperty(name = "Manage Sockets", default = False, description = "Allows to (re)move the input sockets", update = settingChanged)
    hideInputs = BoolProperty(name = "Hide Inputs", default = False, update = settingChanged)

    def create(self):
        self.assignedType = "Float"

    def draw_buttons(self, context, layout):
        self.callFunctionFromUI(layout, "newInputSocket",
            text = "New Input",
            description = "Create a new input socket",
            icon = "PLUS")
        layout.prop(self, "manageSockets")

    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedType", text = "")
        self.callFunctionFromUI(col, "assignSelectedListType",
            text = "Assign",
            description = "Remove all sockets and set the selected socket type")

        layout.prop(self, "hideInputs")

        self.drawTypeSpecificButtonsExt(layout)

    def execute(self, inputs):
        elements = []
        for socket in self.inputs:
            elements.append(inputs[socket.identifier])
        return {"List" : elements}

    def assignSelectedListType(self):
        self.assignedType = self.selectedType

    def assignListType(self, idName, inputAmount = 2):
        self.assignedType = idName
        self.recreateSockets(inputAmount)

    def recreateSockets(self, inputAmount = 2):
        self.inputs.clear()
        self.outputs.clear()

        for i in range(inputAmount):
            self.newInputSocket()
        self.outputs.new(self.listIdName, "List")

    def newInputSocket(self):
        socket = self.inputs.new(self.baseIdName, getNotUsedSocketName(self, "Element"))
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = "Element"
        socket.removeable = self.manageSockets
        socket.moveable = self.manageSockets
        if hasattr(socket, "showName"):
            socket.showName = False
        return socket


    # type specific stuff
    #############################

    def drawTypeSpecificButtonsExt(self, layout):
        if self.assignedType == "Object":
            self.callFunctionFromUI(layout, "createInputsFromSelection", text = "From Selection", icon = "PLUS")

    def createInputsFromSelection(self):
        names = getSortedSelectedObjectNames()
        for name in names:
            socket = self.newInputSocket()
            socket.objectName = name