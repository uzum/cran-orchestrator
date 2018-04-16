from lxml.builder import E
from lxml.etree import tostring
from lxml.etree import Element

def getTargetSwitch(switch):
    namespace = {'inv': 'urn:opendaylight:inventory'}
    node = Element('node', nsmap=namespace)
    node.text = '/inv:nodes/inv:node[inv:id="' + switch + '"]'
    return node

def getBuckets(buckets):
    bucketsClause = E.buckets()
    for bucketIndex, bucket in enumerate(buckets):
        bucketClause = E.bucket()
        bucketClause.append(getattr(E, 'bucket-id')(str(bucketIndex)))
        for actionIndex, action in enumerate(bucket['instructions']):
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
            else:
                raise NotImplementedError('Unsupported action type')
            bucketClause.append(
                E.action(
                    E.order(str(actionIndex)),
                    actionClause
                )
            )
        bucketsClause.append(bucketClause)
    return bucketsClause

class Group():
    nextGroupId = 0

    def __init__(self, options):
        self.options = options
        self.id = Group.nextGroupId
        Group.nextGroupId = Group.nextGroupId + 1

    def xml(self):
        return tostring(E.input(
            E.barrier('false'),
            getTargetSwitch(self.options.get('switch')),
            getattr(E, 'group-id')(str(self.id)),
            getattr(E, 'group-name')('group-' + str(self.id)),
            getattr(E, 'group-type')('group-' + self.options.get('type')),
            getBuckets(self.options.get('buckets')),
            xmlns='urn:opendaylight:group:service'
           ), xml_declaration=True, encoding='UTF-8')
