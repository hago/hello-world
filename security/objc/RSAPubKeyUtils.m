//
//  SecurityUtils.m
//  test
//
//  Created by Chaojun Sun on 13-9-10.
//  Copyright (c) 2013年 Chaojun Sun. All rights reserved.
//

#import "RSAPubKeyUtils.h"
#import <Security/Security.h>

#define DEFAULT_RSA_PUBLIC_KEY_DER "\x30\x82\x03\x02\x30\x82\x01\xea\x02\x09\x00\xb9\x07\xaf\xc8\xea\x56\x9d\xdc\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x42\x31\x1d\x30\x1b\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x09\x01\x16\x0e\x77\x61\x70\x69\x6f\x73\x40\x73\x69\x6e\x61\x2e\x63\x6e\x31\x14\x30\x12\x06\x03\x55\x04\x03\x0c\x0b\x43\x68\x61\x6f\x6a\x75\x6e\x20\x53\x75\x6e\x31\x0b\x30\x09\x06\x03\x55\x04\x06\x13\x02\x43\x4e\x30\x20\x17\x0d\x31\x33\x30\x39\x31\x30\x30\x35\x34\x34\x32\x33\x5a\x18\x0f\x32\x31\x31\x33\x30\x38\x31\x37\x30\x35\x34\x34\x32\x33\x5a\x30\x42\x31\x1d\x30\x1b\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x09\x01\x16\x0e\x77\x61\x70\x69\x6f\x73\x40\x73\x69\x6e\x61\x2e\x63\x6e\x31\x14\x30\x12\x06\x03\x55\x04\x03\x0c\x0b\x43\x68\x61\x6f\x6a\x75\x6e\x20\x53\x75\x6e\x31\x0b\x30\x09\x06\x03\x55\x04\x06\x13\x02\x43\x4e\x30\x82\x01\x22\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x00\x30\x82\x01\x0a\x02\x82\x01\x01\x00\xa1\x7d\xe8\x10\x78\x9a\x1d\x79\x55\xb0\x53\x19\x5d\xa2\xf1\x87\xa0\x7f\xf3\x26\x3e\x26\x8b\x22\x3a\x1a\x47\x70\x44\x65\x7f\xe3\x31\xa2\xe1\x6b\x86\x0c\xf6\x1d\xee\x63\xdf\xff\x72\x5d\xa7\x2a\x87\x35\x52\x8c\xe5\xf9\x4e\xc0\xc5\x4a\x69\x45\x3e\x6a\x41\xa0\x8f\x6a\xb5\xd6\x23\x39\xb0\xc4\x9a\x60\xbc\x67\xda\xf9\x0d\x70\x54\x8c\x57\x58\x01\xce\xa3\x30\xd0\x9e\x81\xe1\x64\xce\x06\x7a\x9b\xf3\x98\x8c\x14\xdd\x77\xe3\x19\x58\xc2\xc0\x58\x22\x23\xfd\x86\xc3\xb6\xf8\x3f\xa6\xe3\x61\x8a\x73\xd5\xf7\x7d\xe7\xc9\x2b\x02\x9a\x45\x80\x3c\x80\x79\xa9\x55\x91\xbd\xea\xfc\x93\xd2\xe9\x0f\xb1\xeb\x88\xe2\xbc\x18\xba\x51\x1f\xa0\x0b\x31\x5a\x90\x1e\x37\x4c\xdd\x5d\x9a\x33\xf5\xa6\xd5\x6a\x63\xe2\x1d\x53\x6a\xa0\x58\x6b\x89\xf0\xa7\x15\xa0\xb2\xea\x49\x21\xae\x5e\x1a\x32\x6c\x48\xdf\x12\xcf\x07\x6b\x67\x01\x1b\x98\xfb\xd4\xbe\x45\xc5\x11\x89\xb8\x00\xe0\x5e\x98\x75\x3e\xb7\x35\xef\x14\x28\x63\x1d\xc2\xed\xc6\x6d\x1b\x70\xdf\x74\xcb\x60\x07\x7d\x62\xd3\x21\xcd\x02\x81\x16\x4c\xae\x8f\x21\xd5\xdc\xe6\x07\xef\x29\xcf\x1a\x2d\x3b\x02\x03\x01\x00\x01\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x03\x82\x01\x01\x00\x4f\x73\xdc\xff\xc4\xb1\x63\x42\xb1\x81\x12\xd1\xa8\x21\xcf\x30\x0e\x6e\x88\xf7\x63\x9a\x54\xc6\x80\x36\xa2\xcb\x27\xeb\x38\x91\x1d\xbf\xd1\x89\x4f\x29\x70\xa5\x50\x28\x02\x54\x91\xba\xa4\x88\x62\xb5\xfd\xbd\x76\x59\x31\x39\x8e\x6e\x4c\x33\x3c\x83\x35\x39\x67\x07\x37\x5d\xa8\x7b\x96\xb7\xa2\xf7\x88\xa8\x57\x16\x56\xde\x48\x24\x89\xb7\xb8\x25\x30\x8f\x20\xa7\xa9\x26\x4f\x13\x4e\x69\x40\x58\xcf\xeb\x78\xe9\x67\xc6\x41\x91\xea\xcb\xbb\x15\xe4\x6c\x25\xbb\x91\xdd\x10\x7b\xe9\x2b\xac\xf7\x4b\xeb\x63\xba\xa3\x70\xe2\xd4\x96\x2b\x7c\x55\x82\x10\xad\x05\x9d\x53\xe8\x0b\xb8\x82\xab\xa8\xbe\x19\x6c\xc8\xef\x4c\x54\x61\xae\x9d\x23\x9d\x99\x8d\x28\x9d\x1c\xa7\x7c\x4f\x01\x90\xd7\xdb\x2d\xdc\x79\xdf\xf0\xfc\xb6\x19\x1b\x6c\x70\xd5\x5e\xae\x73\xae\x74\x25\x6b\x84\x81\xbc\xf9\x29\x35\x34\x8c\x64\x4d\xbf\x97\x5f\x62\x18\xfb\xb5\x9e\x22\x69\xa5\x78\x27\x4b\xe2\x13\x35\x3f\xcf\x66\x96\xee\x85\x2e\x8b\xc3\x49\xf7\x4c\xe0\x25\x51\xcd\xe2\xf7\x25\x6e\x72\xb5\xe9\xab\xd1\x50\xfe\x5a\xf8\xc2\x05\xf2\x6b\xba\x6d\x8b\xda\x7d\xa3\x2c"

#define DEFAULT_RSA_PUBLIC_KEY_DER_LENGTH 774

@interface RSAPubKeyUtils()

-(SecKeyRef)initWithDer:(NSData *)dercontent;

@end

@implementation RSAPubKeyUtils

RSAPubKeyUtils *instance = nil;
NSUInteger maxPlainLength;
SecKeyRef publicKey;

+(RSAPubKeyUtils *)sharedInstance
{
    NSData *dercontent = [NSData dataWithBytes:(const void *)DEFAULT_RSA_PUBLIC_KEY_DER length:DEFAULT_RSA_PUBLIC_KEY_DER_LENGTH];
    return [RSAPubKeyUtils sharedInstance:dercontent];
}

+(RSAPubKeyUtils *)sharedInstance:(NSData *)derPubKeyContent
{
    if (instance == nil) {
        instance = [[RSAPubKeyUtils alloc] init];
        publicKey = [instance initWithDer:derPubKeyContent];
        maxPlainLength = SecKeyGetBlockSize(publicKey) - 12;
    }
    return instance;
}

-(SecKeyRef)initWithDer:(NSData *)dercontent
{
#if __has_feature(objc_arc)
    SecCertificateRef certificate = SecCertificateCreateWithData(kCFAllocatorDefault, ( __bridge CFDataRef)dercontent);
#else
    SecCertificateRef certificate = SecCertificateCreateWithData(kCFAllocatorDefault, (CFDataRef)dercontent);
#endif
    SecPolicyRef policy = SecPolicyCreateBasicX509();
    SecTrustRef trust;
    OSStatus returnCode = SecTrustCreateWithCertificates(certificate, policy, &trust);
    CFRelease(certificate);
    if (returnCode != 0) {
        NSLog(@"SecTrustCreateWithCertificates fail. Error Code: %ld", returnCode);
        [NSException raise:@"init credential error" format:@"SecTrustCreateWithCertificates fail. Error Code: %ld", returnCode];
    }
    SecTrustResultType trustResultType;
    returnCode = SecTrustEvaluate(trust, &trustResultType);
    if (returnCode != 0) {
        NSLog(@"SecTrustEvaluate fail. Error Code: %ld", returnCode);
        [NSException raise:@"init credential error" format:@"SecTrustEvaluate fail. Error Code: %ld", returnCode];
    }
    SecKeyRef pubkey = SecTrustCopyPublicKey(trust);
    if (pubkey == nil) {
        NSLog(@"SecTrustCopyPublicKey fail");
        [NSException raise:@"init credential error" format:@"SecTrustCopyPublicKey fail"];
    }
    
    NSLog(@"so far so good");
    return pubkey;
}

-(NSData *)Encrypt:(NSData *)input
{
    NSMutableData *output = [NSMutableData data];
    const void* buffer = input.bytes;
    uint8_t *cipher = (uint8_t *)malloc((maxPlainLength+12)*sizeof(uint8_t));
    size_t cipherlen;
    for (NSUInteger i = 0; i < input.length; i+=maxPlainLength) {
        NSUInteger len = maxPlainLength;
        if (i+len>input.length) {
            len = input.length - i;
        }
        OSStatus returnCode = SecKeyEncrypt(publicKey, kSecPaddingPKCS1, buffer+i, len, cipher, &cipherlen);
        if (returnCode != 0) {
            NSLog(@"Encrypt fail. Error Code: %ld", returnCode);
            [NSException raise:@"init credential error" format:@"Encrypt fail. Error Code: %ld", returnCode];
        }
        [output appendBytes:(const void *)cipher length:cipherlen];
    }
    free(cipher);
    return output;
}

@end
