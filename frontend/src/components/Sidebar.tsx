import {Link} from 'react-router-dom';

export default function Sidebar(){
	return(
		<>
		<div className="w-64 bg-white shadow-md h-full p-4 flex flex-col gap-2">
			<Link to="/" > Dashboard </Link>
			<Link to="/agent" > New Chat </Link>
			<Link to="/settings" > Settings </Link>
		</div>

		{ /* dynamic load chat history */ }
		</>
	);
}
