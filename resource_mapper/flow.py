from lxml.builder import E
from lxml.etree import tostring
from lxml.etree import Element

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
        elif ('mac-destination' in action):
            actionClause = getattr(E, 'set-dl-dst-action')(
                getattr(E, 'address')(action['mac-destination'])
            )
        elif ('output' in action):
            actionClause = getattr(E, 'output-action')(
                getattr(E, 'output-node-connector')(action['output'])
            )
        elif ('udp-dst-port' in action):
            actionClause = getattr(E, 'set-field')(
                getattr(E, 'udp-destination-port')(action['udp-dst-port'])
            )
        elif ('udp-src-port' in action):
            actionClause = getattr(E, 'set-field')(
                getattr(E, 'udp-source-port')(action['udp-src-port'])
            )
        elif ('group-id' in action):
            actionClause = getattr(E, 'group-action')(
                getattr(E, 'group-id')(action['group-id'])
            )
        else:
            raise NotImplementedError('Unsupported action type')
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

    def xml(self, pretty=False):
        return tostring(E.input(
            E.barrier('false'),
            getTargetSwitch(self.options.get('switch')),
            E.cookie(str(self.id)),
            E.flags('SEND_FLOW_REM'),
            getattr(E, 'hard-timeout')(self.options.get('hard-timeout')),
            getattr(E, 'idle-timeout')(self.options.get('idle-timeout')),
            E.installHw('false'),
            getFilters(self.options.get('filters')),
            getInstructions(self.options.get('instructions')),
            E.priority(self.options.get('priority')),
            E.strict('false'),
            getattr(E, 'table_id')(self.options.get('table_id')),
            xmlns='urn:opendaylight:flow:service'
           ), xml_declaration=True, encoding='UTF-8', pretty_print=pretty)
