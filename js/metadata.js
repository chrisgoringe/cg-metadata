import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

// Displays input text on a node

app.registerExtension({
	name: "cg.ShowText",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "Show Text" || nodeData.name === "Show Metadata") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);

				if (this.widgets) {
					const pos = this.widgets.findIndex((w) => w.name === "text");
					if (pos !== -1) {
						for (let i = pos; i < this.widgets.length; i++) {
							this.widgets[i].onRemove?.();
						}
						this.widgets.length = pos;
					}
				}

				//for (const list of message.text) {
					const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;
					w.inputEl.readOnly = true;
					w.inputEl.style.opacity = 0.6;
					w.value = message.text.join('');
				//}

				this.onResize?.(this.size);
			};
		}
	},
});

app.registerExtension({
	name: "cg.SendText",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "Set Widget Value") {
			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				onExecuted?.apply(this, arguments);
                const node_index = parseInt(message.node_id.join(''));
                const widget_name = message.widget_name.join('');
				const widget_index = this.graph._nodes_by_id[node_index].widgets.findIndex((w) => w.name===widget_name);
				if (node_index>=0 && widget_index>=0) {
					this.graph._nodes_by_id[node_index].widgets[widget_index].value = message.text.join('');
				}
			};
		}
	},
});

