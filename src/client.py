import asyncio
from fastmcp import Client



client = Client("http://localhost:8000/mcp")
async def main():
    async with client:

        print("CONNECTED")

        templates = await client.list_resource_templates()

        print("TEMPLATE COUNT:", len(templates))

        for template in templates:
            print(template)

asyncio.run(main())