from langchain_core.runnables.graph import MermaidDrawMethod
from builder import multi_agentic_graph


image_data = multi_agentic_graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)

with open('photo/graph_image.png', 'wb') as file:
    file.write(image_data)
