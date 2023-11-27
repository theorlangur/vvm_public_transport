// VVM Transport Timetable Card

class VVMTransportTimetableCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({
            mode: 'open'
        });
    }

    /* This is called every time sensor is updated */
    set hass(hass) {

        const config = this.config;
        const maxEntries = config.max_entries || 10;
        const showStopName = config.show_stop_name || (config.show_stop_name === undefined);
        const entityIds = config.entity ? [config.entity] : config.entities || [];
        const show_cancelled = false;

        let type_to_color = {
            "Bus":"#0000FF",
            "Straßenbahn":"#FF8000",
        }
        let type_to_label = {
            "Bus":"Bus",
            "Straßenbahn":"Str"
        }

        let content = "";

        for (const entityId of entityIds) {
            const entity = hass.states[entityId];
            if (!entity) {
                throw new Error("Entity State Unavailable");
            }

            const isStale = 'stale' in entity.attributes ? entity.attributes['stale'] : true
            const lastUpdateSimple = 'last_updated_simple' in entity.attributes ? entity.attributes['last_updated_simple'] : ''

            if (showStopName) {
                content += `<div class="stop">${entity.attributes.stop_name}${isStale ? '(' + lastUpdateSimple + ')' : ''}</div>`;
            }

            const staleColorStyle = isStale ? `style="color: #808080"` : '';

            const departures = 'departures' in entity.attributes ? entity.attributes.departures : []
            const timetable = departures.slice(0, maxEntries).map((departure) => 
                `   <div class="line">
                        <div class="line-icon" style="background-color: ${type_to_color[departure.type] || "#404040"}">${type_to_label[departure.type] || departure.type} ${departure.num}</div>
                    </div>
                    <div class="direction">${departure.to}</div>
                    <div class="time" ${staleColorStyle}>${departure.left}${departure.delay > 0 ? '(+' + departure.delay + ')' : ''}'</div>
                    <div class="time" ${staleColorStyle}>${departure.real_time_simple}</div>
                `
            );

            content += `<div class="departures">` + timetable.join("\n") + `</div>`;
        }

       this.shadowRoot.getElementById('container').innerHTML = content;
    }

    /* This is called only when config is updated */
    setConfig(config) {
        const root = this.shadowRoot;
        if (root.lastChild) root.removeChild(root.lastChild);

        this.config = config;

        const card = document.createElement('ha-card');
        const content = document.createElement('div');
        const style = document.createElement('style')
  
        style.textContent = `
            .container {
                padding: 10px;
                font-size: 130%;
                line-height: 1.5em;
            }
            .stop {
                opacity: 0.6;
                font-weight: 400;
                width: 100%;
                text-align: left;
                padding: 10px 10px 5px 5px;
            }      
            .departures {
                width: 100%;
                font-weight: 400;
                line-height: 1.5em;
                padding-bottom: 20px;
                display: grid;
                grid-template-columns: min-content 1fr min-content min-content;
                gap: 10px;
            }
            .line {
                min-width: 70px;
                text-align: right;
            }
            .line-icon {
                display: inline-block;
                border-radius: 20px;
                padding: 7px 10px 5px;
                font-size: 100%;
                font-weight: 500;
                line-height: 1em;
                color: #FFFFFF;
                text-align: center;
            }
            .direction {
                justify-self: start;
                flex-grow: 1;
            }
            .time {
                font-weight: 700;
                line-height: 2em;
                padding-right: 10px;
                justify-self: start;
            }
        `;
     
        content.id = "container";
        content.className = "container";
        card.header = config.title;
        card.appendChild(style);
        card.appendChild(content);

        root.appendChild(card);
      }
  
    // The height of the card.
    getCardSize() {
      return 5;
    }
}
  
customElements.define('vvm-transport-timetable-card', VVMTransportTimetableCard);
