Vue.component('history-entry', {
  props: ['entry'],
  template: `
    <div class="history-item">{{ JSON.stringify(this.entry) }}</div>
  `
})

Vue.component('log-history', {
  props: ['history'],
  template: `
    <div class="history-container">
      <history-entry
        v-for="entry in history"
        v-bind:key="entry.timestamp"
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
      console.log('peeking');
      axios.get(`${LCServerURL}/peek?index=${this.lastSeenIndex}`)
        .then((response) => {
          response.data.forEach(entry => {
            this.history.push(entry);
            if (this.history.length > HISTORY_CAPACITY) this.history.unshift();
          });
          setTimeout(this.peek, PEEK_INTERVAL);
        })
        .catch((error) => {
          console.log(error);
          setTimeout(this.peek, PEEK_INTERVAL);
        });
    }
  }
});
