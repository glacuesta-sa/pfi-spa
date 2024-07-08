import { useEffect, useState } from "react";
import type { Schema } from "../amplify/data/resource";
import { generateClient } from "aws-amplify/data";
import CustomAppBar from "./components/Appbar";
import Dendogram from "./components/Dendogram";
import TreeMap from "./components/TreeMap";

const client = generateClient<Schema>();

function App() {
  const [todos, setTodos] = useState<Array<Schema["Todo"]["type"]>>([]);

  useEffect(() => {
    client.models.DendogramNode.observeQuery().subscribe({
      next: (data) => setTodos([...data.items]),
    });
  }, []);

  function createTodo() {
    client.models.Todo.create({ content: window.prompt("Todo content") });
  }

  return (
    <main>
      <CustomAppBar/>
      <Dendogram/>
      <TreeMap/>
    </main>
  );
}

export default App;
