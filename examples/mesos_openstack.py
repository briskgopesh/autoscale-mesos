#!/usr/bin/env python
import argparse
import logging
import sys

from autoscale import MesosReporter, MesosDecider, AwsAsgScaler

# cinder create --source-volid 60624506-ac29-4079-969e-5119628fa110 --display-name ms-01 10
# nova boot --boot-volume c3c5f294-8c3c-4be1-bfe1-f3b8d29ac403 --key-name macdsa --flavor small ms-01
#
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log-level', default="warn",
                        help='Log level (debug, [default] info, warn, error)')
    parser.add_argument('-u', '--mesos-url', help='Mesos cluster URL', required=True)
    parser.add_argument('-c', '--cpus', help='Comma-delimited CPU thresholds '
                                             '(lower,upper)')
    parser.add_argument('-d', '--disk', help='Comma-delimited disk thresholds '
                                             '(lower,upper)')
    parser.add_argument('-m', '--mem', help='Comma-delimited memory thresholds '
                                            '(lower,upper)')
    parser.add_argument('-os-host', '--os-host', help='OpenStack identity '
                                                   'endpoint',
                        required=True)
    parser.add_argument('os-tenant_id', '--os-tenant_id', help = 'OpenStack '
                                                                 'tenant ID')
    parser.add_argument('os-user_id', '--os-tenant_id', help = 'OpenStack '
                                                                 'user name')
    parser.add_argument('os-password', '--os-tenant_id', help = 'OpenStack '
                                                                 'password')

    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stderr, level=getattr(logging, args.log_level.upper()))

    thresholds = {}
    if args.cpus:
        lower, upper = args.cpus.split(',')
        thresholds['cpus'] = dict(lower=int(lower), upper=int(upper))
    if args.disk:
        lower, upper = args.disk.split(',')
        thresholds['disk'] = dict(lower=int(lower), upper=int(upper))
    if args.mem:
        lower, upper = args.mem.split(',')
        thresholds['mem'] = dict(lower=int(lower), upper=int(upper))

    reporter = MesosReporter(args.mesos_url)
    decider = MesosDecider(thresholds)
    scaler = OpenStackScaler(args.region, args.asg)
    
    delta = decider.should_scale(reporter)
    if delta:
        print 'Scaling {asg} in {region} by {delta}'.format(asg=args.asg, region=args.region, delta=delta)
        scaler.scale(delta)
    else:
        print 'No change needed for {asg} in {region}'.format(asg=args.asg, region=args.region)


if __name__ == '__main__':
    main()