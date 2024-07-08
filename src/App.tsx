// import { useEffect, useState } from "react";
// import type { Schema } from "../amplify/data/resource";
// import { generateClient } from "aws-amplify/data";
import CustomAppBar from "./components/Appbar";
import Dendogram from "./components/Dendogram";
import TreeMap from "./components/TreeMap";

// const client = generateClient<Schema>();

function App() {
  // const [nodes, setNodes] = useState<Array<Schema["DendogramNode"]["type"]>>([]);

  // useEffect(() => {
  //   client.models.DendogramNode.observeQuery().subscribe({
  //     next: (data) => setNodes([...data.items]),
  //   });
  // }, []);



  return (
    <main>
      <CustomAppBar/>
      <Dendogram/>
      <TreeMap/>
      <iframe width="600" height="450" src="https://lookerstudio.google.com/embed/reporting/16a3d95e-a2ad-4e39-bdf5-74eac4593ec4/page/twIoD" sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
    </main>
  );
}

export default App;
