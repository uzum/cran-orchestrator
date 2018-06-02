const RMServerURL = '/resource-mapper';

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
        controllerNode: '',
        computeNodes: []
      }
    };
  },
  created: function(){
    this.update();
  },
  methods: {
   update: function(){}
  }
});
