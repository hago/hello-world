//
//  SecurityUtils.h
//  test
//
//  Created by Chaojun Sun on 13-9-10.
//  Copyright (c) 2013年 Chaojun Sun. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface SecurityUtils : NSObject

+(SecurityUtils *)sharedInstance;
-(NSData *)RSA_Encrypt:(NSData *)input;
-(NSData *)RSA_Encrypt:(NSData *)input DerPublicKey:(NSData *)dercontent;

@end
