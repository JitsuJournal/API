# System
import uuid
# Local
from ..models.general import Node, Edge, Technique
from ..models.reactflow import Node as FlowNode
from ..models.reactflow import NodeData
from ..models.reactflow import Edge as FlowEdge, Reactflow
# Third Party

def shape_nodes(nodes: list[Node]) -> tuple[dict[int,str], list[FlowNode]]:
    """
    Given a list of Node objects, this function
    iterates over each item and reshapes them to fit
    react-flow and jitsu-journal's initialNodes structure.

    It also additionally returns a idMap used to keep
    edge's source and target ID's consistent with generated UUID's
    """

    # Initialize dict for storing a map of node IDs and their generated UUIDs
    # used to ensure edges reference the generated ID's
    idMap = {}

    # Update nodes shape and store in initialNodes list
    initialNodes = []
    for node in nodes:
        # Node id's need to be UUIDs
        generatedId = str(uuid.uuid4())
        # To ensure this change ripples to edges, 
        # we need store the UUID in a ID map
        idMap[node.id] = generatedId

        # Flatten tags for react-flow.js
        tags = [tag.model_dump() for tag in node.technique.tags]
        
        # Create and append object replacing current node
        # as initial node for react-flow
        flowNode = FlowNode(id=generatedId, data=
            NodeData(
                technique_id=node.technique.id,
                name=node.technique.name,
                tags=tags,
                cat_id=node.technique.cat_id
            )
        )
        initialNodes.append(flowNode)

    return idMap, initialNodes

def shape_edges(idMap: dict, edges: list[Edge]) -> list[FlowEdge]:
    """
    Given a list of Edge objects, this function
    iterates over each item and reshapes them to fit
    react-flow and jitsu-journal's initialEdges structure.

    To ensure that source/target ID's match updated node IDs,
    an ID map is required {old: new}.
    """
    # Update edges shape and store in initialEdges list
    initialEdges = []
    for edge in edges: 
        # Use ID map to reference the node UUID's
        sourceId = idMap[edge.source_id]
        targetId = idMap[edge.target_id]

        # Generate a new edge ID based on the format below:
        # - xy-edge__sourceID-sourceHandle_targetID-targetHandle
        generatedId = f"xy-edge__{sourceId}-b_{targetId}-a"


        flowEdge = FlowEdge(
            id=generatedId, source=sourceId, target=targetId, 
            data={'note': edge.note}
        )
        initialEdges.append(flowEdge)

    return initialEdges


if __name__=="__main__":
    # Mock raw nodes with techinque objects in them
    # NOTE: Tags are passed in as dicts and then converted
    # to avoid errors related to PyDantic v2 updates
    singleLeg = Node(id=1, technique=
        Technique(
            id=83,
            name="Single Leg",
            description="A takedown where the attacker secures one of the opponent's legs and uses different finishes like running the pipe, lifting, or switching to a double-leg.",
            tags=[
                {"id": 22, "name": "wrestling"},
            ],
            cat_id=3
        )
    )
    fullGuard = Node(id=2, technique=
        Technique(
            id=16,
            name="Full Guard",
            description="Maintaining an open guard position with legs not locked, using feet, knees, and grips to control distance and create opportunities for sweeps and submissions.",
            tags=[
                {"id": 3, "name": "bottom"},
                {"id": 4, "name": "open"}
            ],
            cat_id=1
        )
    )
    halfGuard = Node(id=3, technique=
        Technique(
            id=20,
            name="Half Guard",
            description="Controlling one of the opponent's legs between your legs, focusing on creating space, sweeping, or transitioning to full guard or a better position.",
            tags=[
                {"id": 3, "name": "bottom"}
            ],
            cat_id=1
        )
    )
    ankleLock = Node(id=4, technique=
        Technique(
            id=45,
            name="Ankle Lock",
            description="A leg lock that hyperextends the ankle joint, typically applied by grasping the ankle and applying pressure with the forearm.",
            tags=[
                {"id": 9, "name": "ankle"}
            ],
            cat_id=2
        )
    )
    omoplata = Node(id=5, technique=
        Technique(
            id=42,
            name="Omoplata",
            description="A shoulder lock that uses the legs to apply pressure on the opponent's shoulder joint, often set up from guard positions.",
            tags=[
                {"id": 11, "name": "shoulder"}
            ],
            cat_id=2
        )
    )
    kneeBar = Node(id=6, technique=
        Technique(
            id=43,
            name="Knee Bar",
            description="A leg lock that hyperextends the knee joint, applied by trapping the opponent's leg between your legs and pulling back on the heel.",
            tags=[
                {"id": 13, "name": "knee"}
            ],
            cat_id=2
        )
    )
    scissorSweep = Node(id=7, technique=
        Technique(
            id=48,
            name="Scissor Sweep",
            description="A sweep from guard where the legs scissor to off-balance and flip the opponent, transitioning to mount.",
            tags=[
                {"id": 3, "name": "bottom"}
            ],
            cat_id=3
        )
    )
    sideControl = Node(id=8, technique=
        Technique(
            id=9,
            name="Standard Side Control",
            description="Controlling the opponent from the side while pinning their shoulders and hips, maintaining pressure with chest-to-chest contact.",
            tags=[
                {"id": 2, "name": "seated"},
                {"id": 1, "name": "top"}
            ],
            cat_id=1
        )
    )
    armBar = Node(id=9, technique=
        Technique(
            id=39,
            name="Arm Bar",
            description="A joint lock that hyperextends the elbow joint, typically applied by trapping the opponent's arm between your legs and pulling on the wrist while pushing with the hips.",
            tags=[
                {"id": 12, "name": "elbow"}
            ],
            cat_id=2
        )
    )

    rawNodes: list[Node] = [singleLeg, fullGuard, halfGuard, ankleLock, 
             omoplata, kneeBar, scissorSweep, sideControl, armBar]

    # Test reshaping the nodes into PyDantic objects
    idMap, initialNodes = shape_nodes(rawNodes)
    #print(initialNodes)

    # Mock raw edges (ensuring only edges with source id in idMap/rawNodes exists below)
    e1 = Edge(id=1, source_id=1, target_id=2, note="Establish a strong single leg X-guard from open guard")
    e2 = Edge(id=2, source_id=2, target_id=3, note="Transition from single leg X to cross ashi garami or ankle-lace ashi garami")
    e3 = Edge(id=3, source_id=3, target_id=4, note="Attack with an Achilles lock from ankle lace ashi garami")
    e4 = Edge(id=4, source_id=4, target_id=5, note="If the opponent defends the Achilles lock, transition to an inside heel hook")
    e5 = Edge(id=5, source_id=5, target_id=6, note="If the opponent's hips come up or they drive forward, shift your hips to transition to the saddle position")
    e6 = Edge(id=6, source_id=5, target_id=7, note="If the opponent defends the initial heel hook, re-entangle")
    e7 = Edge(id=8, source_id=7, target_id=8, note="sweep them to a dominant top position")
    e8 = Edge(id=9, source_id=8, target_id=9, note="From a dominant top position, re-attack the legs")

    rawEdges = [e1, e2, e3, e4, e5, e6, e7, e8]

    # Test reshaping the edges into PyDantic objects
    initialEdges = shape_edges(idMap, rawEdges)


    # Create the react-flow object
    # and test dumping it to see how the user would receive
    graph = Reactflow(initialNodes=initialNodes,initialEdges=initialEdges)
    print(graph.model_dump())