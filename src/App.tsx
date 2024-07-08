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
    </main>
  );
}

export default App;
