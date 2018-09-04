const classes = ['primary', 'secondary', 'dark', 'light', 'info', 'warning', 'success', 'danger'];
const assignedClasses = new Map();

Vue.component('history-entry', {
  props: ['entry'],
  template: `
    <div class="history-item row">
      <div class="col-md-2">
        <span class="badge badge-light">{{ entry.timestamp }}</span>
      </div>
      <div class="col-md-2">
        <span v-bind:class="sourceClass">{{ entry.source }}</span>
      </div>
      <div class="col-md-8">
        <code>{{ payload }}</code>
      </div>
    </div>
  `,
  computed: {
    payload: function(){
      const object = {};
      Object.keys(this.entry).forEach(key => {
        if (key !== 'timestamp' && key !== 'source') {
          object[key] = this.entry[key];
        }
      });
      return object;
    },
    sourceClass: function(){
      if (assignedClasses.has(this.entry.source)) {
        return assignedClasses.get(this.entry.source);
      } else {
        const assignedClass = `badge badge-${classes[Math.floor(Math.random() * classes.length)]}`;
        assignedClasses.set(this.entry.source, assignedClass);
        return assignedClass;
      }
    }
  }
});

Vue.component('log-history', {
  props: ['history'],
  template: `
    <div class="history-container">
      <div class="row">
        <div class="col-md-2"><b>Timestamp</b></div>
        <div class="col-md-2"><b>Source</b></div>
        <div class="col-md-2"><b>Payload</b></div>
      </div>
      <history-entry
        v-for="entry in history"
        v-bind:key="entry.timestamp + entry.source"
        v-bind:entry="entry"
      />
    </div>
  `
});

const HISTORY_CAPACITY = 10;
const PEEK_INTERVAL = 3000;

const LC = new Vue({
  el: '#lc-vue-app',
  data: function(){
    return {
      lastSeenIndex: 0,
      history: []
    };
  },
  created: function(){
    this.peek();
  },
  methods: {
    peek: function(){
      axios.get(`${LCServerURL}/peek?index=${this.lastSeenIndex}`)
        .then((response) => {
          response.data.forEach(entry => {
            this.history.push(entry);
            if (this.history.length > HISTORY_CAPACITY) this.history.shift();
          });
          setTimeout(this.peek, PEEK_INTERVAL);
          this.lastSeenIndex += response.data.length;
        })
        .catch((error) => {
          console.log(error);
          setTimeout(this.peek, PEEK_INTERVAL);
        });
    }
  }
});
