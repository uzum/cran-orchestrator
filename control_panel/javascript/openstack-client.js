const OCServerURL = '/openstack-client';
const CONTROLLER_HOSTNAME = '5G-1'

Vue.component('instance', {
  props: ['instance'],
  template: `
    <div>
      <hr>
      <b>{{ instance.name }}</b><br />
      <b>ID:</b> {{ instance.id }}<br />
      <b>Status:</b> {{ instance.status }}<br />
      <b>Addresses:</b><br />
      <p v-for="address in instance.addresses" v-bind:address="address">
        <b>{{ address.type }}:</b> {{ address.addr }}<br />
      </p>
      <button class="btn btn-danger" v-on:click="deleteInstance">Delete</button>
      <hr>
    </div>
    `,
  methods: {
    deleteInstance: function(){
      this.$emit('delete', this.instance.name);
    },
    migrate: function(){}
  }
})

Vue.component('hypervisor', {
  props: ['hypervisor'],
  template: `
    <div class="col-md-12">
      <div class="card border-info" style="margin-bottom: 20px;">
        <div class="card-header" v-bind:class="hypervisorClass">
          <b>Hypervisor#{{ hypervisor.id }}</b><br />
        </div>
        <div class="card-body">
          <p>
            <b>Hostname: </b><span>{{ hypervisor.hostname }}</span><br />
            <b>IP: </b><span>{{ hypervisor.host_ip }}</span>
          </p>
          <ul class="list-group list-group-flush">
            <li
              class="hypervisor-list-item"
              is="instance"
              v-for="instance in hypervisor.instances"
              v-bind:instance="instance"
              v-bind:key="instance.id"
              v-on:change="update"
              v-on:delete="deleteInstance"
            ></li>
            <li v-if="!hypervisor.isController">
              <div class="input-group">
                <input v-model="hypervisor.newInstance.name" type="text" class="form-control" placeholder="Instance name">
                <div class="input-group-append">
                  <button class="btn btn-outline-secondary" type="button" v-on:click="createInstance">Create new</button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  `,
  computed: {
    hypervisorClass: function(){
      return {
        'bg-info': !this.hypervisor.isController,
        'bg-secondary': this.hypervisor.isController
      };
    }
  },
  methods: {
    createInstance: function(){
      axios.post(`${OCServerURL}/instance?name=${this.hypervisor.newInstance.name}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    update: function(){
      this.$emit('change');
    },
    deleteInstance: function(instanceName){
      axios.post(`${OCServerURL}/instance/${instanceName}/delete`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    }
  }
});

const OC = new Vue({
  el: '#oc-vue-app',
  data: function(){
    return {
      hypervisors: []
    };
  },
  computed: {
    orderedHypervisors: function(){
      return this.hypervisors.sort((a, b) => a.hostname.localeCompare(b.hostname));
    }
  },
  created: function(){
    this.update();
  },
  methods: {
    update: function(){
      axios.get(`${OCServerURL}/hypervisor/all`).then((response) => {
        while (this.hypervisors.length) this.hypervisors.pop();
        return Promise.all(response.data.map((hypervisor) => {
          return axios.get(`${OCServerURL}/hypervisor/${hypervisor.hostname}/instances`)
            .then((hvResponse) => {
              this.hypervisors.push(Object.assign({
                instances: hvResponse.data,
                newInstance: { name: '' },
                isController: hypervisor.hostname === CONTROLLER_HOSTNAME
              }, hypervisor));
            });
        }));
      }).catch(function(error){
        console.log(error);
      });
    }
  }
});
