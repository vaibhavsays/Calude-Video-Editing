import React from 'react';
import {Composition} from 'remotion';
import {Main, INSERTS} from './Main';

const FPS = 30;

export const Root: React.FC = () => (
  <>
    <Composition
      id="Main"
      component={Main}
      durationInFrames={1002}
      fps={FPS}
      width={1080}
      height={1920}
    />
    {INSERTS.map((ins) => (
      <Composition
        key={ins.id}
        id={ins.id}
        component={ins.Component}
        durationInFrames={Math.round((ins.to - ins.from) * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
      />
    ))}
  </>
);
