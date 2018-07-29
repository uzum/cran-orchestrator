const OCServerURL = '/openstack-client';

Vue.component('instance', {
  props: ['instance'],
  template: `
    <hr>
    <b>{{ instance.name }}</b><br />
    <b>ID:</b> {{ instance.id }}<br />
    <b>Status:</b> {{ instance.status }}<br />
    <b>Addresses:</b><br />
    <p v-for="address in instance.addresses">
      <b>{{ address.type }}:</b> {{ address.addr }}<br />
    </p>
    <button class="btn btn-danger" v-on:click="delete">Delete</button>
    <hr>
    `,
  methods: {
    delete: function(){
      this.$emit('delete', this.name);
    },
    migrate: function(){}
  }
})

Vue.component('hypervisor', {
  props: ['hypervisor'],
  template: `
    <div class="col-md-12">
      <div class="card border-info" style="margin-bottom: 20px;">
        <div class="card-header">
          <b>Hypervisor#{{ hypervisor.id }}</b><br />
          <b>Hostname: </b><span>{{ hypervisor.hostname }}</span><br />
          <b>IP: </b><span>{{ hypervisor.host_ip }}</span>
        </div>
        <div class="card-body">
          <ul class="list-group list-group-flush">
            <li
              is="instance"
              v-for="instance in hypervisor.instances"
              v-bind:instance="instance"
              v-bind:key="instance.id"
              v-on:change="update"
              v-on:delete="deleteInstance"
            ></li>
            <li>
              <div class="input-group">
                <input v-model="newInstance.name" type="text" class="form-control" placeholder="Instance name">
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
  methods: {
    createInstance: function(){
      axios.post(`${OCServerURL}/instance/create?name=${this.newInstance.name}`)
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
      hypervisors: [],
      newInstance: {
        name: ''
      }
    };
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
                instances: hvResponse.data
              }, hypervisor));
            });
        }));
      }).catch(function(error){
        console.log(error);
      });
    }
  }
});
