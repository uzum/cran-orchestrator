const RMServerURL = '/resource-mapper';

Vue.component('openstack-host', {
  props: ['host'],
  template: `
    <div style="padding: 5px; margin-bottom: 10px; background-color: rgba(0,0,0,.03)">
      <p>
        <span style="width: 100%; font-size: 16px;" class="badge badge-info">Host#{{ host.id }}</span>
      </p>
      <p>
        <b>IP: </b><span>{{ host.ip }}</span>
      </p>
      <p>
        <b>MAC: </b><span>{{ host.mac }}</span>
      </p>
    </div>
  `
});

Vue.component('openstack-node', {
  props: ['node', 'type', 'candidate'],
  template: `
    <div class="col-md-6">
      <div class="card" style="margin-bottom: 20px">
        <div class="card-header">
          <b>{{ node.id }}</b><br />
          <span
            class="badge" v-bind:class="badgeClass">{{ type }}</span>
        </div>
        <div class="card-body">
          <openstack-host v-for="host in node.hosts" v-bind:host="host" />
        </div>
        <button v-if="candidate" class="btn btn-primary" type="button" v-on:click="setControllerNode">
          Set controller
        </button>
      </div>
    </div>
  `,
  computed: {
    badgeClass: function(){
      return {
        'badge-danger': this.type === 'controller',
        'badge-dark': this.type === 'compute'
      };
    }
  },
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

Vue.component('new-mapping', {
  props: ['rule'],
  template: `
    <div class="col-md-12">
      <div class="card">
        <div class="card-header">
          <b>Create new mapping</b>
        </div>
        <div class="card-body">
          <b>RRH ID: </b>
          <div class="input-group">
            <input class="form-control" type="text" v-model="rule.rrh" />
            <div class="input-group-append">
              <button class="btn btn-primary" type="button" v-on:click="create">Create</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  methods: {
    create: function(){
      this.$emit('create', this.rule);
    }
  }
});

Vue.component('mapping', {
  props: ['rule'],
  template: `
    <div class="col-md-12">
      <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
          <b>RRH#{{ rule.rrh }}</b> <span class="badge badge-dark">Rule#{{ rule.id }}</span>
          <button type="button" class="close" v-on:click="remove">&times;</button>
        </div>
        <div class="card-body">
          <div class="row">
            <div v-for="bbuId in rule.bbus" class="col-md alert alert-warning"
              style="margin-right: 10px; font-size: 14px; box-sizing: initial;">
              <b>BBU#{{ bbuId }}</b>
              <span
                style="cursor: pointer; font-weight: bold; float: right;"
                v-on:click="removeBBU(bbuId)">
                  &times;
              </span>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="input-group">
            <input class="form-control" type="text" v-model="newBBUId" />
            <div class="input-group-append">
              <button style="margin-right: 20px;" class="btn btn-warning" type="button" v-on:click="addBBU(newBBUId)">Add BBU</button>
            </div>
            <button v-if="rule.id !== -1" class="btn btn-info" type="button" v-on:click="update">Update</button>
            <button v-if="rule.id === -1" class="btn btn-success" type="button" v-on:click="create">Create</button>
          </div>
        </div>
      </div>
    </div>
  `,
  data: function(){
    return {
      newBBUId: 0
    }
  },
  methods: {
    remove: function(){
      axios.post(`${RMServerURL}/mapping/${this.rule.id}/remove`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    addBBU: function(bbuId){
      if (this.rule.bbus.indexOf(bbuId) === -1) {
        this.rule.bbus.push(bbuId);
      }
    },
    removeBBU: function(bbuId){
      this.rule.bbus = this.rule.bbus.filter(id => id !== bbuId);
    },
    update: function(){
      axios.post(`${RMServerURL}/mapping/${this.rule.id}/update?bbus=${this.rule.bbus.join(',')}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    create: function(){
      axios.post(`${RMServerURL}/mapping?rrh=${this.rule.rrh}&bbus=${this.rule.bbus.join(',')}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    }
  }
});

Vue.component('mapping-list', {
  props: ['mappings', 'newMapping'],
  template: `
    <div class="row">
      <h3>Current mapping: </h3>
      <mapping
        v-for="mapping in mappings"
        v-bind:key="mapping.id"
        v-bind:rule="mapping"
        v-on:change="onMappingChange"
      />
      <new-mapping
        v-bind:rule="newMapping"
        v-on:create="onMappingCreate"
      />
    </div>
  `,
  methods: {
    onMappingChange: function(){
      this.$emit('change');
    },
    onMappingCreate: function(rule){
      this.mappings.push(rule);
    }
  }
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
        id: -1,
        rrh: -1,
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
