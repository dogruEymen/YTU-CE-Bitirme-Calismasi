import type {ChatResponse} from './../types/chat-response.ts'

export default async function fetchDataWithTimeout(url: string, timeout = 10000){
	const controller = new AbortController();
	const timer = setTimeout(() => {
		controller.abort();
	}, timeout);

	try{
		const res = await fetch(url, {
			signal: controller.signal
		});

		if(!res.ok){
			throw new Error("HTTP " + res.status);
		}		

		return await res.json();
	}
	// }catch(error){
	// 	if(error.name === 'AbortError'){
	// 		console.log("Request timed out !");
	// 	}else{
	// 		console.log("Error: ", error);
	// 	}
	// }
	finally{
		clearTimeout(timer);
	}
}

export async function postMessage(
	url: string, 
	message: string
): Promise<ChatResponse>{

	const response = await fetch(url, {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			message: message
		})
	});
	
	if(!response.ok){
		throw new Error(`HTTP ${response.status}`);
	}

	const data: ChatResponse = await response.json();

	return data;
}
