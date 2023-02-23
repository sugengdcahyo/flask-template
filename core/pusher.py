import pusher
import os

"""pusher_client = pusher.Pusher(
  app_id=os.environ.get('PUSHER_APP_ID'),
  key=os.environ.get('PUSHER_KEY'),
  secret=os.environ.get('PUSHER_SECRET'),
  cluster=os.environ.get('PUSHER_CLUSTER'),
  ssl=str(os.environ.get('PUSHER_SSL')).lower() in ('true', '1', 't')
)"""

pusher_poxa = pusher.Pusher(
  app_id="app_id",
  key="app_key",
  secret="secret",
)
# pusher_client = pusher.Pusher(
#   app_id='1540942',
#   key='408162a5cb0a91fbaa2c',
#   secret='97beb80fa962073dccc9',
#   cluster='ap1',
#   ssl=True
# )
