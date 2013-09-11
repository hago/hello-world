package com.lucropia.security.demo;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.math.BigInteger;

import com.lucropia.security.*;

public class TestApp {

	/**
	 * @param args
	 * @throws LucropiaException
	 * @throws UnsupportedEncodingException
	 */
	public static void main(String[] args) throws UnsupportedEncodingException,
			LucropiaException {
		validateEncrypt();
	}

	public static void validateEncrypt() throws UnsupportedEncodingException,
			LucropiaException {
		BigInteger modulus = new BigInteger(
				"A17DE810789A1D7955B053195DA2F187A07FF3263E268B223A1A477044657FE331A2E16B860CF61DEE63DFFF725DA72A8735528CE5F94EC0C54A69453E6A41A08F6AB5D62339B0C49A60BC67DAF90D70548C575801CEA330D09E81E164CE067A9BF3988C14DD77E31958C2C0582223FD86C3B6F83FA6E3618A73D5F77DE7C92B029A45803C8079A95591BDEAFC93D2E90FB1EB88E2BC18BA511FA00B315A901E374CDD5D9A33F5A6D56A63E21D536AA0586B89F0A715A0B2EA4921AE5E1A326C48DF12CF076B67011B98FBD4BE45C51189B800E05E98753EB735EF1428631DC2EDC66D1B70DF74CB60077D62D321CD0281164CAE8F21D5DCE607EF29CF1A2D3B",
				16);
		BigInteger exponent = new BigInteger("65537", 10);
		String s = "abc";
		byte[] buf;
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < 255; i++) {
			sb.append(s);
		}
		buf = RSAUtils.encryptRSAPublicKey(s, modulus, exponent);
		System.out.printf("static short string ok, result length: %d\r\n",
				buf.length);
		writeFile("jssmall.enc", buf);
		buf = RSAUtils.encryptRSAPublicKey(sb.toString(), modulus, exponent);
		System.out.printf("static long string ok, result length: %d\r\n",
				buf.length);
		writeFile("jsbig.enc", buf);

		RSAUtils ru = new RSAUtils(modulus, exponent);
		buf = ru.encryptPublicKey(s);
		System.out.printf("short string ok, result length: %d\r\n", buf.length);
		writeFile("jsmall.enc", buf);

		buf = ru.encryptPublicKey(sb.toString());
		System.out.printf("long string ok, result length: %d\r\n", buf.length);
		writeFile("jbig.enc", buf);
	}
	
	static void writeFile(String filename, byte[] content) {
		try {
			FileOutputStream fs = new FileOutputStream(filename);
			fs.write(content);
			fs.close();
		} catch (FileNotFoundException e) {
			System.err.printf("FileNotFoundException: %s\r\n", e.getMessage());
		} catch (IOException e) {
			System.err.printf("IOException: %s\r\n", e.getMessage());
		}
	}

}
