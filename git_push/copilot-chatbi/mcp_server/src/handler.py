import os
from abs import ThreadCorsHandler
import json

class MCPIntensionHandler(ThreadCorsHandler):
    
    def initialize(self, mcpclient):
        self.mcpclient = mcpclient

    async def process_func(self,session_id, request_id, query):
        await self.mcpclient.connect_to_server(os.path.dirname(os.path.abspath(__file__)) + "/intension_mcp_tools.py")
        answer = await self.mcpclient.process_query(query)
        response_data = {
            "session_id": session_id,
            "request_id": request_id,
            "answer": answer
        }
        return response_data

    async def post(self):
        try:
            data = json.loads(self.request.body)
            session_id = data.get("session_id")
            request_id = data.get("request_id")
            query = data.get("query")

            if not query:
                self.set_status(400)
                self.write({"error": "Missing 'query' in request data"})
                return

            try:
                response_data = await self.process_func(session_id, request_id, query)
                self.set_status(200)
                self.write(response_data)
            except Exception as e:
                self.set_status(500)
                print(e)
                self.write({"error": str(e)})
            finally:
                await self.mcpclient.cleanup()
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON data in request"})
