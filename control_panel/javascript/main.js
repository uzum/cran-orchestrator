const LGServerURL = 'http://127.0.0.1:5001';

Vue.component('RemoteRadioHead', {
  template: `
    <div class="card">
      <div class="card-header">RRH#{{ rrh.id }}</div>
      <div class="card-body">
        <p>Number of connections: {{ rrh.connections.length }}</p>
        <p>Packet generation rate: {{ rrh.arrivalRate }}</p>
        <p>Target UDP Port: {{ rrh.dstPort }}</p>
      </div>
      <div class="card-footer"></div>
    </div>
  `,
  props: ['rrh'],
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
    addConnection: function(amount){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/add-connection?amount=${amount}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    removeConnection: function(){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/remove-connection?amount=${amount}`)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    setRateParameter: function(rate){
      axios.post(`${LGServerURL}/rrh/${this.rrh.id}/set-arrival-rate?rate=${rate}`)
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
      rrhs: []
    };
  },
  created: function(){
    this.update();
  },
  methods: {
    addRRH: function(rrhParams){
      axios.post(`${LGServerURL}/rrh/create`, rrhParams)
        .then((response) => {
          this.$emit('change');
        })
        .catch(function(error){
          console.log(error);
        });
    },
    update: function(){
      axios.get(`${LGServerURL}/configuration`)
        .then((response) => {
          this.rrhs = response;
        })
        .catch(function(error){
          console.log(error);
        });
    },
  }
});
