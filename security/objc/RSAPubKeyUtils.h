//
//  SecurityUtils.h
//  test
//
//  Created by Chaojun Sun on 13-9-10.
//  Copyright (c) 2013年 Chaojun Sun. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface RSAPubKeyUtils : NSObject

+(RSAPubKeyUtils *)sharedInstance;
+(RSAPubKeyUtils *)sharedInstance:(NSData *)derPubKeyContent;
-(NSData *)Encrypt:(NSData *)input;

@end
