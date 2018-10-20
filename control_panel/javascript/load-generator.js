Vue.component('new-remote-radio-head', {
  template: `
    <div class="col-md-3">
      <div class="card" style="margin-bottom: 20px;">
        <div class="card-header bg-secondary">
          <b>Create new RRH</b>
        </div>
        <div class="card-body">
          <b>Poisson rate: </b>
          <div class="input-group">
            <input class="form-control" type="text" v-model="rrh.arrivalRate" />
            <div class="input-group-append">
              <button class="btn btn-primary" type="button" v-on:click="create">Create</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  props: ['rrh'],
  methods: {
    create: function(){
      axios.post(`${LGServerURL}/rrh/create?rate=${this.rrh.arrivalRate}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    }
  }
});

Vue.component('remote-radio-head', {
  template: `
    <div class="col-md-3">
      <div class="card" style="margin-bottom: 20px;">
        <div class="card-header bg-warning">
          <b>RRH#{{ rrh.id }}</b>
          <button type="button" class="close" v-on:click="remove">&times;</button>
        </div>
        <div class="card-body">
          <p><b>Target UDP Port: </b>{{ rrh.dstPort }}</p>
          <hr>
          <p>
            <span class="badge" v-bind:class="badgeClass">{{ rrh.state }}</span>
            <div class="btn-group" role="group">
              <button type="button" class="btn btn-light" v-on:click="start">Start</button>
              <button type="button" class="btn btn-light" v-on:click="stop">Stop</button>
            </div>
          </p>
          <p>
            <b>Connections: </b>
            <span>{{ rrh.connections.length }}</span>
            <button v-on:click="removeConnection" type="button" style="border-radius: 50%;" class="btn btn-primary">-</button>
            <button v-on:click="addConnection" type="button" style="border-radius: 50%;" class="btn btn-primary">+</button>
          </p>
          <hr>
          <p>
            <b>Poisson rate: </b>
            <div class="input-group">
              <input class="form-control" type="text" v-model="rrh.arrivalRate" />
              <div class="input-group-append">
                <button class="btn btn-primary" type="button" v-on:click="setRateParameter">Set</button>
              </div>
            </div>
          </p>
            <b>Packet size mean: </b>
            <div class="input-group">
              <input class="form-control" type="text" v-model="rrh.packetSizeMean" />
              <div class="input-group-append">
                <button class="btn btn-primary" type="button" v-on:click="setDistributionParameter('packetSizeMean')">Set</button>
              </div>
            </div>
          </p>
            <b>Packet size dev.: </b>
            <div class="input-group">
              <input class="form-control" type="text" v-model="rrh.packetSizeDev" />
              <div class="input-group-append">
                <button class="btn btn-primary" type="button" v-on:click="setDistributionParameter('packetSizeDev')">Set</button>
              </div>
            </div>
          </p>
        </div>
        <div class="card-footer">
          <div v-for="connection in rrh.connections">
            <span>{{ connection.name }} seq#: </span><b>{{ connection.sequenceNumber }}</b>
          </div>
        </div>
      </div>
    </div>
  `,
  props: ['rrh'],
  computed: {
    badgeClass: function(){
      return this.rrh.state === 'running' ? 'badge-success' : 'badge-dark';
    }
  },
  methods: {
    remove: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/remove`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    addConnection: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/add-connection?amount=1`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    removeConnection: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/remove-connection?amount=1`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    setRateParameter: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/set-arrival-rate?rate=${this.rrh.arrivalRate}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    setDistributionParameter: function(param){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/set-parameter/${param}?value=${this.rrh[param]}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    start: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/start`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    stop: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/stop`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    }
  }
});

const LG = new Vue({
  el: '#lg-vue-app',
  data: function(){
    return {
      rrhs: [],
      newRrh: {
        arrivalRate: 0,
        packetSizeMean: 0,
        packetSizeDev: 0
      }
    };
  },
  created: function(){
    this.update();
  },
  methods: {
    update: function(){
      axios.get(`${LGServerURL}/configuration`)
        .then((response) => {
          while (this.rrhs.length) this.rrhs.pop();
          response.data.forEach(rrh => this.rrhs.push(rrh));
        })
        .catch(function(error){
          console.log(error);
        });
    },
  }
});
