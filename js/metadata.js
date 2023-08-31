import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

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

