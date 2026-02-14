import * as route53 from 'aws-cdk-lib/aws-route53';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as targets from 'aws-cdk-lib/aws-route53-targets';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface CustomDomainProps {
    domainName: string;
    api: apigateway.RestApi;
}

export class CustomDomain extends Construct {
    public readonly hostedZone: route53.IHostedZone;
    public readonly certificate: acm.Certificate;
    public readonly customDomain: apigateway.DomainName;

    constructor(scope: Construct, id: string, props: CustomDomainProps) {
        super(scope, id);

        this.hostedZone = new route53.PublicHostedZone(this, 'HostedZone', {
            zoneName: props.domainName,
        });

        (this.hostedZone as route53.PublicHostedZone).applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);

        this.certificate = new acm.Certificate(this, 'Certificate', {
            domainName: props.domainName,
            validation: acm.CertificateValidation.fromDns(this.hostedZone),
        });

        this.customDomain = new apigateway.DomainName(this, 'CustomDomain', {
            domainName: props.domainName,
            certificate: this.certificate,
            endpointType: apigateway.EndpointType.REGIONAL,
        });

        this.customDomain.addBasePathMapping(props.api, {
            basePath: '',
        });

        new route53.ARecord(this, 'AliasRecord', {
            zone: this.hostedZone,
            recordName: props.domainName,
            target: route53.RecordTarget.fromAlias(
                new targets.ApiGatewayDomain(this.customDomain)
            ),
        });
    }
}