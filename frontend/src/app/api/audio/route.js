import { NextResponse } from 'next/server';

export async function POST(req) {
  return NextResponse.json({
    text: "Speech recognition is handled in the browser",
    success: true
  });
}

