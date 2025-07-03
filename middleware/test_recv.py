from Node import Node

if __name__ == "__main__":
    node: Node = Node(
        process_id=1,
        seconds=10
    )
    
    node.main()