import {Outlet} from 'react-router-dom';
import Sidebar from './../components/Sidebar.tsx'

function MainLayout(){
	return(
		<div className="flex h-screen w-screen">
			<Sidebar/>

      		<div className="flex-1 p-4 bg-gray-50 overflow-auto">
				<Outlet />
			</div>
		</div>
	);
}

export default MainLayout;
