const RMServerURL = '/resource-mapper';

Vue.component('openstack-node', {
  props: ['node', 'type', 'candidate'],
  template: `
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">
          <b>Node#{{ node.id }} - {{ type }}</b>
        </div>
        <div class="card-body">
          <div v-for="host in node.hosts">
            <span><b>Host#{{ host.id }}: {{ host.ip }}/{{ host.mac }}</b></span>
          </div>
        </div>
        <button v-if="candidate" class="btn btn-primary" type="button" v-on:click="setControllerNode">
          Set controller
        </button>
      </div>
    </div>
  `,
  methods: {
    setControllerNode: function(){
      axios.post(`${RMServerURL}/topology/set-controller?id=${this.node.id}`)
        .then((response) => {
          this.$emit('topology-change');
        })
        .catch(function(error){
          console.log(error);
        });
    }
  }
});

Vue.component('mapping', {
  props: ['rule'],
  template: `
    <div>mapping</div>
  `
});

Vue.component('topology', {
  props: ['topology'],
  template: `
    <div class="row">
      <openstack-node
        v-if="topology.controllerNode"
        v-bind:node="topology.controllerNode"
        type="controller"
        v-bind:candidate="false"
      />
      <openstack-node
        type="compute"
        v-for="node in topology.computeNodes"
        v-bind:key="node.id"
        v-bind:node="node"
        v-on:topology-change="onTopologyChange"
        v-bind:candidate="!topology.controllerNode"
      />
    </div>
  `,
  methods: {
    onTopologyChange: function(){
      this.$emit('change');
    }
  }
});

const RM = new Vue({
  el: '#rm-vue-app',
  data: function(){
    return {
      mappings: [],
      newMapping: {
        rrh: 0,
        bbus: []
      },
      topology: {
        controllerNode: null,
        computeNodes: []
      }
    };
  },
  created: function(){
    this.updateTopology();
    this.updateMapping();
  },
  methods: {
    updateTopology: function(){
      axios.get(`${RMServerURL}/topology`)
        .then((response) => {
          while (this.topology.computeNodes.length) this.topology.computeNodes.pop();
          response.data.computeNodes.forEach(node => this.topology.computeNodes.push(node));
          this.topology.controllerNode = response.data.controllerNode;
        })
        .catch(function(error){
          console.log(error);
        });
    },
    updateMapping: function(){
      axios.get(`${RMServerURL}/mapping/all`)
        .then((response) => {
          while (this.mappings.length) this.mappings.pop();
          response.data.forEach(mapping => this.mappings.push(mapping));
        })
        .catch(function(error){
          console.log(error);
        });
    }
  }
});
