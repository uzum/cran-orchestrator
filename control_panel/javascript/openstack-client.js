const OCServerURL = '/openstack-client';

Vue.component('instance', {
  props: ['instance'],
  template: `
    <span>{{ instance.name }}</span>
  `,
  created: function(){
    console.log(this.instance);
  },
  methods: {
    remove: function(){},
    migrate: function(){}
  }
})

Vue.component('hypervisor', {
  props: ['hypervisor'],
  template: `
    <div class="col-md-6">
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
              v-on:change="update()"
            ></li>
          </ul>
        </div>
      </div>
    </div>
  `,
  methods: {
    addInstance: function(name){},
    update: function(){
      this.$emit('change');
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
  created: function(){
    this.update();
  },
  methods: {
    update: function(){
      axios.get(`${OCServerURL}/hypervisor/all`).then((hypervisors) => {
        while (this.hypervisors.length) this.hypervisors.pop();
        return Promise.map(hypervisors, (hypervisor) => {
          return axios.get(`${OCServerURL}/hypervisor/${hypervisor.hostname}/instances`)
            .then((instances) => {
              this.hypervisors.push(Object.assign({ instances }, hypervisor));
            });
        });
      }).catch(function(error){
        console.log(error);
      });
    }
  }
});
