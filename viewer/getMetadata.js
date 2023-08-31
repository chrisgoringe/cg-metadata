function getPngMetadata(file) {
	return new Promise((r) => {
		const reader = new FileReader();
		reader.onload = (event) => {
			// Get the PNG data as a Uint8Array
			const pngData = new Uint8Array(event.target.result);
			const dataView = new DataView(pngData.buffer);

			// Check that the PNG signature is present
			if (dataView.getUint32(0) !== 0x89504e47) {
				console.error("Not a valid PNG file");
				r();
				return;
			}

			// Start searching for chunks after the PNG signature
			let offset = 8;
			let txt_chunks = {};
			// Loop through the chunks in the PNG file
			while (offset < pngData.length) {
				// Get the length of the chunk
				const length = dataView.getUint32(offset);
				// Get the chunk type
				const type = String.fromCharCode(...pngData.slice(offset + 4, offset + 8));
				if (type === "tEXt") {
					// Get the keyword
					let keyword_end = offset + 8;
					while (pngData[keyword_end] !== 0) {
						keyword_end++;
					}
					const keyword = String.fromCharCode(...pngData.slice(offset + 8, keyword_end));
					// Get the text
					const contentArraySegment = pngData.slice(keyword_end + 1, offset + 8 + length);
					const contentJson = Array.from(contentArraySegment).map(s=>String.fromCharCode(s)).join('')
					txt_chunks[keyword] = contentJson;
				}

				offset += 12 + length;
			}

			r(txt_chunks);
		};

		reader.readAsArrayBuffer(file);
	});
}

async function handleFile(file) {
    const pngInfo = await getPngMetadata(file);
    var result = "<table>"
	if (typeof pngInfo !== 'undefined' && typeof pngInfo['cg'] !== 'undefined') {
    	info = JSON.parse(pngInfo['cg'], function (key, value) { if (key) {result += "<tr><th>"+key+"</th><td>"+value+"</td></tr>" }})
	} else {
		result += "<tr><th>No metadata with tag 'cg'</th></tr>"
	};
	result += "</table>";
    document.getElementById('results').innerHTML = result;
	document.getElementById('preview').src = URL.createObjectURL(file);
}

function when_loaded() {
    document.getElementById('file-input').onchange = async () => {
        await this.handleFile(document.getElementById('file-input').files[0]);
    }
	document.getElementById('container').addEventListener(
		"drop",
		async (e) => {
		  e.preventDefault();
		  e.stopPropagation();
		  await this.handleFile(e.dataTransfer.files[0]);
		},
		false
	  );
}
