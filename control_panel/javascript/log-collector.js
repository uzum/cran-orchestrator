const HISTORY_CAPACITY = 20;
const PEEK_INTERVAL = 1000;
const STATS_INTERVAL = 5000;

const ColorCoder = (function(){
  const colorSet = ['primary', 'secondary', 'dark', 'light', 'info', 'warning', 'success', 'danger']
  let available = colorSet.slice(0);
  const assignments = new Map();

  return {
    get: function(source){
      if (assignments.has(source)) return assignments.get(source);

      // make a new assignment
      const color = available.shift();
      assignments.set(source, color);
      if (available.length === 0) {
        available = colorSet.slice(0);
      }
      return color;
    },
    release: function(source){
      if (!assignments.has(source)) return;
      const color = assignments.get(source);
      assignments.delete(source);
      available.push(color);
    }
  }
})();

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
      return `badge badge-${ColorCoder.get(this.entry.source)}`;
    }
  }
});

Vue.component('log-history', {
  props: ['history'],
  data: function(){
    return {
      query: ''
    };
  },
  template: `
    <div class="history-container">
      <div class="row">
        <h5>log history</h5>
        <div class="row container">
          <div class="col-md-3">
            <b>Filter by: </b>
            <div class="input-group">
              <input type="text" class="form-control" v-model="query">
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-2"><b>Timestamp</b></div>
        <div class="col-md-2"><b>Source</b></div>
        <div class="col-md-2"><b>Payload</b></div>
      </div>
      <history-entry
        v-for="entry in filteredHistory"
        v-bind:key="entry.timestamp + entry.source"
        v-bind:entry="entry"
      />
    </div>
  `,
  computed: {
    filteredHistory: function(){
      return this.history
        .filter(entry => entry.source.includes(this.query))
        .sort((a, b) => b.timestamp - a.timestamp);
    }
  }
});

Vue.component('source-stats', {
  props: ['source'],
  data: function(){
    return {
      timeout: null,
      stats: [],
      dataCount: 0,
      hover: ''
    };
  },
  template: `
    <div class="col-md-3">
      <div class="card border-danger">
        <div class="card-header bg-danger">
          <b>{{ source }}</b><span> (Data points: {{ this.dataCount }})</span>
          <a><i class="fas fa-times float-right" style="cursor: pointer;" v-on:click="removeSource"></i></a>
        </div>
        <div class="card-body source-stats-body">
          <div v-for="stat in stats">
            <b v-on:mouseover="hover = stat.attr;">{{ stat.attr }}:</b><span> &mu; = {{ stat.value['mean'].toFixed(3) }}</span>
            <div v-show="hover == stat.attr">
              <span class="badge badge-light" v-for="value in stat.value['last5']"> {{ value.toFixed(3) }} </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  created: function(){
    this.update();
  },
  methods: {
    update: function(){
      axios.get(`${LCServerURL}/stats?source=${this.source}&limit=30`)
        .then((response) => {
          // first empty the previous stats array
          while (this.stats.length) this.stats.pop();

          Object.keys(response.data).forEach(attr => {
            if (attr === 'count') {
              this.dataCount = response.data.count;
              return;
            }
            this.stats.push({
              attr,
              value: response.data[attr]
            });
          });
          this.timeout = setTimeout(this.update, STATS_INTERVAL);
        })
        .catch((error) => {
          console.log(error);
          this.timeout = setTimeout(this.update, STATS_INTERVAL);
        });
    },
    removeSource: function(){
      clearTimeout(this.timeout);
      this.$emit('removal', this.source);
    }
  }
});

Vue.component('stat-panel', {
  data: function(){
    return {
      observedSources: [],
      newSource: ''
    }
  },
  template: `
    <div class="row">
      <h5>source based statistics</h5>
      <div class="row container">
        <source-stats
          v-for="source in observedSources"
          v-bind:key="source"
          v-bind:source="source"
          v-on:removal="remove(source)"
        ></source-stats>
        <div class="col-md-3">
          <b>Observe source: </b>
          <div class="input-group">
            <input class="form-control" type="text" v-model="newSource" />
            <div class="input-group-append">
              <button class="btn btn-primary" type="button" v-on:click="observe">Observe</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  methods: {
    observe: function(){
      this.observedSources.push(this.newSource);
      this.newSource = '';
    },
    remove: function(source){
      const idx = this.observedSources.lastIndexOf(source);
      if (idx !== -1) {
        this.observedSources.splice(idx, 1);
      }
    }
  }
});

const LC = new Vue({
  el: '#lc-vue-app',
  data: function(){
    return {
      lastSeenTimestamp: 0,
      history: []
    };
  },
  created: function(){
    this.peek();
  },
  methods: {
    peek: function(){
      axios.get(`${LCServerURL}/peek?timestamp=${this.lastSeenTimestamp}`)
        .then((response) => {
          response.data.forEach(entry => {
            this.history.push(entry);
            if (this.history.length > HISTORY_CAPACITY) this.history.shift();
          });
          setTimeout(this.peek, PEEK_INTERVAL);

          // update the last seen timestamp for next peek request
          if (response.data[0]) {
            this.lastSeenTimestamp = response.data[0].timestamp;
          }
        })
        .catch((error) => {
          console.log(error);
          setTimeout(this.peek, PEEK_INTERVAL);
        });
    }
  }
});
