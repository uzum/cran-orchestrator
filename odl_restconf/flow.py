from lxml.builder import E
from lxml.etree import tostring
from lxml.etree import Element

HARD_TIMEOUT = getattr(E, 'hard-timeout')
IDLE_TIMEOUT = getattr(E, 'idle-timeout')
TABLE_ID = getattr(E, 'table_id')

PROTOCOL_MAP = {
    'udp': '17',
    'icmp': '1'
}

def getTargetSwitch(switch):
    namespace = {'inv': 'urn:opendaylight:inventory'}
    node = Element('node', nsmap=namespace)
    node.text = '/inv:nodes/inv:node[inv:id="' + switch + '"]'
    return node

def getFilters(filters):
    clause = E.match()
    if ('ethernet' in filters):
        clause.append(
            getattr(E, 'ethernet-match')(
                getattr(E, 'ethernet-type')(
                    E.type(filters['ethernet'])
                )
            )
        )

    if ('ip' in filters):
        clause.append(getattr(E, 'ip-match')(
            getattr(E, 'ip-protocol')(PROTOCOL_MAP[filters['ip']['protocol']])
        ))
        if ('destination' in filters['ip']):
            clause.append(
                getattr(E, 'ipv4-destination')(filters['ip']['destination'])
            )
        if ('source' in filters['ip']):
            clause.append(
                getattr(E, 'ipv4-source')(filters['ip']['source'])
            )

    if ('udp' in filters):
        if ('source-port' in filters['udp']):
            clause.append(
                getattr(E, 'udp-source-port')(filters['udp']['source-port'])
            )
        if ('destination-port' in filters['udp']):
            clause.append(
                getattr(E, 'udp-destination-port')(filters['udp']['destination-port'])
            )

    return clause

def getInstructions(instructions):
    actions = getattr(E, 'apply-actions')()
    for index, action in enumerate(instructions):
        actionClause = None
        if ('ip-destination' in action):
            actionClause = getattr(E, 'set-nw-dst-action')(
                getattr(E, 'ipv4-address')(action['ip-destination'])
            )
        if ('mac-destination' in action):
            actionClause = getattr(E, 'set-dl-dst-action')(
                getattr(E, 'address')(action['mac-destination'])
            )
        if ('output' in action):
            actionClause = getattr(E, 'output-action')(
                getattr(E, 'output-node-connector')(action['output'])
            )
        if ('udp-dst-port' in action):
            actionClause = getattr(E, 'set-field')(
                getattr(E, 'udp-destination-port')(action['udp-dst-port'])
            )
        if ('udp-src-port' in action):
            actionClause = getattr(E, 'set-field')(
                getattr(E, 'udp-source-port')(action['udp-src-port'])
            )
        actions.append(
            E.action(
                E.order(str(index)),
                actionClause
            )
        )

    return E.instructions(
        E.instruction(
            E.order('0'),
            actions
        )
    )

class Flow():
    nextFlowId = 0

    def __init__(self, options):
        self.options = options
        self.id = Flow.nextFlowId
        Flow.nextFlowId = Flow.nextFlowId + 1

    def xml(self):
        return tostring(E.input(
                E.barrier('false'),
                getTargetSwitch(self.options.get('switch')),
                E.cookie(str(self.id)),
                E.flags('SEND_FLOW_REM'),
                HARD_TIMEOUT(self.options.get('hard-timeout')),
                IDLE_TIMEOUT(self.options.get('idle-timeout')),
                E.installHw('false'),
                getFilters(self.options.get('filters')),
                getInstructions(self.options.get('instructions')),
                E.priority(self.options.get('priority')),
                E.strict('false'),
                TABLE_ID(self.options.get('table_id')),
                xmlns='urn:opendaylight:flow:service'
               ), xml_declaration=True, encoding='UTF-8')
