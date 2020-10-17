import boto3
from mcstatus import MinecraftServer


def main():
    start_stop_mc()

def start_stop_mc():
    ec2 = boto3.resource('ec2')
    # instances = boto3.client('ec2').describe_instances()
    # print_dict(instances)
    mc = ec2.Instance('i-024979d60d4edfc94')
    resp = mc.start(DryRun=False)
    dd(resp)
    mc.wait_until_running()
    dd("Instance is running now!")
    ip = str(mc.public_ip_address)
    dd("IP: " + ip)
    elastic_ip_to_instance('i-024979d60d4edfc94')
    dd("IP is bound")
    wait_for_mc_on('mcbingo.squareplayn.com')
    dd("Minecraft is running now!")
    wait_for_player_count('mcbingo.squareplayn.com', 1)
    dd("Someone joined!")
    wait_for_player_count('mcbingo.squareplayn.com', 0)
    dd("Server empty!")
    resp = mc.stop()
    dd(resp)
    elastic_ip_to_instance('i-0c334cc3d5d72892b')
    dd("IP bound back")
    mc.wait_until_stopped()
    dd("Instance is fully stopped")


def elastic_ip_to_instance(instance_id):
    dd("Swapping IP to instance " + instance_id)
    boto3.client('ec2').associate_address(
        InstanceId=instance_id,
        PublicIp='18.157.155.213',
        AllowReassociation=True,
        DryRun=False,
    )


def dd(msg=""):
    print("=" * 30)
    print_dict(msg)
    print("=" * 30)


def wait_for_mc_on(ip):
    dd("Waiting for " + ip + " to turn on MC")
    on = False
    while not on:
        on = check_mc_on(ip)


def wait_for_player_count(ip, count):
    dd("Waiting for " + str(count) + " players on " + ip)
    player_count = count + 1
    while player_count != count:
        player_count = get_mc_player_count(ip)


def check_mc_on(ip):
    try:
        r = MinecraftServer.lookup(ip).status()
        dd(r)
        return True
    except Exception as e:
        return False


def get_mc_player_count(ip):
    return MinecraftServer.lookup(ip).status().players.online


def print_dict(values, indent=0):
    if isinstance(values, list):
        for value in values:
            print_dict(value, indent + 4)
    elif isinstance(values, dict):
        for key in values:
            value = values[key]
            row = " " * indent + str(key) + " => "
            if not (isinstance(value, list) or isinstance(value, dict)):
                print(row + str(value))
            else:
                print(row)
                print_dict(value, indent + 4)
    else:
        print(" " * indent + str(values))


if __name__ == '__main__':
    main()
